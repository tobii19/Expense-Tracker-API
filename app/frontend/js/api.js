// Centralized API Client for Expense Tracker Backend

const API = (function() {
  const getBaseUrl = () => {
    // If hosted together or on custom port, use current origin or localhost fallback
    if (window.location.origin && window.location.origin.includes("http")) {
      return window.location.origin;
    }
    return "http://127.0.0.1:8000";
  };

  const getToken = () => localStorage.getItem("expense_tracker_token");
  const setToken = (token) => localStorage.setItem("expense_tracker_token", token);
  const removeToken = () => localStorage.removeItem("expense_tracker_token");

  async function request(endpoint, options = {}) {
    const url = `${getBaseUrl()}${endpoint}`;
    const token = getToken();
    
    const headers = {
      ...options.headers
    };

    if (token && !options.skipAuth) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    try {
      const response = await fetch(url, { ...options, headers });
      
      if (response.status === 401) {
        removeToken();
        window.dispatchEvent(new Event("auth:unauthorized"));
        throw new Error("Session expired. Please log in again.");
      }

      const data = await response.json().catch(() => ({}));
      
      if (!response.ok) {
        let errorMsg = `HTTP Error ${response.status}`;
        if (Array.isArray(data.detail)) {
          errorMsg = data.detail.map(item => `${item.loc ? item.loc[item.loc.length - 1] + ': ' : ''}${item.msg || 'invalid field'}`).join("; ");
        } else if (typeof data.detail === "string") {
          errorMsg = data.detail;
        } else if (typeof data.detail === "object" && data.detail !== null) {
          errorMsg = JSON.stringify(data.detail);
        } else if (data.message) {
          errorMsg = data.message;
        }
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err.message);
      throw err;
    }
  }

  return {
    getToken,
    setToken,
    removeToken,
    isAuthenticated: () => !!getToken(),

    // Auth
    async login(email, password) {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const res = await request("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
        skipAuth: true
      });

      if (res.access_token) {
        setToken(res.access_token);
      }
      return res;
    },

    async register(name, email, password) {
      return request("/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
        skipAuth: true
      });
    },

    async verifyOTP(email, otp) {
      const res = await request("/auth/verify-otp", {
        method: "POST",
        body: JSON.stringify({ email, otp }),
        skipAuth: true
      });
      if (res.access_token) {
        setToken(res.access_token);
      }
      return res;
    },

    async resendOTP(email) {
      return request("/auth/resend-otp", {
        method: "POST",
        body: JSON.stringify({ email }),
        skipAuth: true
      });
    },

    async forgotPassword(email) {
      return request("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
        skipAuth: true
      });
    },

    async resetPassword(email, otp, newPassword) {
      return request("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({ email, otp, new_password: newPassword }),
        skipAuth: true
      });
    },

    async getMe() {
      return request("/auth/me");
    },

    async deleteUser(email) {
      return request(`/auth/delete-users?email=${encodeURIComponent(email)}`, {
        method: "DELETE"
      });
    },

    async updateUser(name, email, password) {
      return request("/update-user/profile", {
        method: "PUT",
        body: JSON.stringify({ name, email, password })
      });
    },

    // Dashboard
    async getDashboard() {
      return request("/dashboard/");
    },

    // Transactions
    async getTransactions() {
      return request("/transaction/");
    },

    async getTransactionByName(name) {
      return request(`/transaction/${encodeURIComponent(name)}`);
    },

    async createTransaction(transactionData) {
      const payload = {
        name: transactionData.name,
        type: transactionData.type,
        amount: parseFloat(transactionData.amount),
        description: transactionData.description || "",
        customer_type: transactionData.customer_type || "standard"
      };

      return request("/transaction/", {
        method: "POST",
        body: JSON.stringify(payload)
      });
    },

    async getPaginatedTransactions(page = 1, pageSize = 10) {
      return request(`/pagination/?page=${page}&page_size=${pageSize}`);
    },

    async searchTransactions(query) {
      return request(`/pagination/search?search=${encodeURIComponent(query)}`);
    },

    // Reports
    async getSpendReport() {
      return request("/report/spends");
    },

    async getMonthlyReport(month, year, type = "") {
      let url = `/report/monthly?month=${month}&year=${year}`;
      if (type) url += `&type=${type}`;
      return request(url);
    },

    async getSortedTransactions(sortBy = "date", sortOrder = "desc") {
      return request(`/report/sortby?sort_by=${sortBy}&sort_order=${sortOrder}`);
    },

    async getDateRangeTransactions(startDate, endDate, type = "") {
      let url = `/report/date_range?start_date=${startDate}&end_date=${endDate}`;
      if (type) url += `&type=${type}`;
      return request(url);
    },

    async getAmountTotal(startDate, endDate, type = "") {
      let url = `/report/amount_total?start_date=${startDate}&end_date=${endDate}`;
      if (type) url += `&type=${type}`;
      return request(url);
    },

    // Download Report (returns a Blob for file download)
    async downloadMonthlyExcel(startDate, endDate) {
      const url = `${getBaseUrl()}/report-downlaod/export-monthly?start_date=${startDate}&end_date=${endDate}`;
      const token = getToken();
      const response = await fetch(url, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!response.ok) {
        let errMsg = `HTTP Error ${response.status}`;
        try {
          const errData = await response.json();
          errMsg = typeof errData.detail === "string" ? errData.detail : errMsg;
        } catch (_) {}
        throw new Error(errMsg);
      }
      return response.blob();
    }
  };
})();
