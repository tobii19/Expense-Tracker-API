// SpendWise — App Controller
document.addEventListener("DOMContentLoaded", () => {
  // ── Global State ────────────────────────────────────────
  let currentPage = 1;
  let pageSize = 8;
  let currentSortBy = "date";
  let currentSortOrder = "desc";
  let currentUser = null;
  let searchTimeout = null;
  let pendingVerificationEmail = "";
  let resendCountdownInterval = null;
  let authMode = "login"; // 'login' | 'register'

  // ── Auth Section Elements ────────────────────────────────
  const authSection        = document.getElementById("authSection");
  const mainAppSection     = document.getElementById("mainAppSection");

  // Tabs & main login/register form
  const authTabs           = document.getElementById("authTabs");
  const loginTab           = document.getElementById("loginTab");
  const registerTab        = document.getElementById("registerTab");
  const authForm           = document.getElementById("authForm");
  const nameGroup          = document.getElementById("nameGroup");
  const authSubmitBtn      = document.getElementById("authSubmitBtn");
  const authBtnText        = document.getElementById("authBtnText");
  const authTitle          = document.getElementById("authTitle");

  // Step indicator
  const stepIndicator = document.getElementById("stepIndicator");
  const step1Item     = document.getElementById("step1Item");
  const step2Item     = document.getElementById("step2Item");
  const step3Item     = document.getElementById("step3Item");

  // OTP screen (now a div, not a form)
  const otpScreen          = document.getElementById("otpScreen");
  const otpForm            = document.getElementById("otpForm");
  const otpInput           = document.getElementById("otpInput");
  const otpTargetEmail     = document.getElementById("otpTargetEmail");
  const resendOtpBtn       = document.getElementById("resendOtpBtn");
  const resendTimer        = document.getElementById("resendTimer");
  const backToLoginFromOtp = document.getElementById("backToLoginFromOtp");

  // Forgot password screen
  const forgotPasswordLink     = document.getElementById("forgotPasswordLink");
  const forgotScreen           = document.getElementById("forgotScreen");
  const forgotStep1            = document.getElementById("forgotStep1");
  const forgotStep2            = document.getElementById("forgotStep2");
  const forgotEmailInput       = document.getElementById("forgotEmail");
  const sendResetOtpBtn        = document.getElementById("sendResetOtpBtn");
  const resetOtpInput          = document.getElementById("resetOtpInput");
  const newPasswordInput       = document.getElementById("newPasswordInput");
  const submitResetPasswordBtn = document.getElementById("submitResetPasswordBtn");
  const backToLoginFromForgot  = document.getElementById("backToLoginFromForgot");

  // ── Dashboard Elements ───────────────────────────────────
  const userNameEl      = document.getElementById("userName");
  const userEmailEl     = document.getElementById("userEmail");
  const userAvatarEl    = document.getElementById("userAvatar");
  const logoutBtn       = document.getElementById("logoutBtn");
  const totalBalanceEl  = document.getElementById("totalBalance");
  const totalIncomeEl   = document.getElementById("totalIncome");
  const totalExpenseEl  = document.getElementById("totalExpense");
  const highestExpenseEl = document.getElementById("highestExpense");
  const lowestExpenseEl  = document.getElementById("lowestExpense");
  const totalTxCountEl   = document.getElementById("totalTxCount");

  // Spend gauge
  const spendProgressBar  = document.getElementById("spendProgressBar");
  const spendRatioPercent = document.getElementById("spendRatioPercent");
  const spendIncomeLabel  = document.getElementById("spendIncomeLabel");
  const spendExpenseLabel = document.getElementById("spendExpenseLabel");

  // Transaction table & toolbar
  const transactionsTableBody = document.getElementById("transactionsTableBody");
  const searchInput   = document.getElementById("searchInput");
  const sortSelect    = document.getElementById("sortSelect");
  const pageSizeSelect = document.getElementById("pageSizeSelect");
  const prevPageBtn   = document.getElementById("prevPageBtn");
  const nextPageBtn   = document.getElementById("nextPageBtn");
  const currentPageBadge = document.getElementById("currentPageBadge");

  // Transaction modals
  const txModal           = document.getElementById("txModal");
  const openAddTxBtn      = document.getElementById("openAddTxBtn");
  const closeTxModal      = document.getElementById("closeTxModal");
  const txForm            = document.getElementById("txForm");
  const txDetailModal     = document.getElementById("txDetailModal");
  const closeTxDetailModal = document.getElementById("closeTxDetailModal");
  const txDetailContent   = document.getElementById("txDetailContent");

  // Date range modal
  const dateRangeModal      = document.getElementById("dateRangeModal");
  const openDateRangeModalBtn = document.getElementById("openDateRangeModalBtn");
  const closeDateRangeModal = document.getElementById("closeDateRangeModal");
  const drStartDate  = document.getElementById("drStartDate");
  const drEndDate    = document.getElementById("drEndDate");
  const drType       = document.getElementById("drType");
  const applyDateRangeBtn = document.getElementById("applyDateRangeBtn");
  const drMinAmount  = document.getElementById("drMinAmount");
  const drMaxAmount  = document.getElementById("drMaxAmount");
  const drCount      = document.getElementById("drCount");
  const drResultsBody = document.getElementById("drResultsBody");

  // Settings modal
  const settingsModal      = document.getElementById("settingsModal");
  const openSettingsBtn    = document.getElementById("openSettingsBtn");
  const closeSettingsModal = document.getElementById("closeSettingsModal");
  const settingsForm       = document.getElementById("settingsForm");
  const deleteAccountBtn   = document.getElementById("deleteAccountBtn");

  // Monthly report
  const reportMonthInput  = document.getElementById("reportMonth");
  const reportYearInput   = document.getElementById("reportYear");
  const reportTypeFilter  = document.getElementById("reportTypeFilter");
  const fetchReportBtn    = document.getElementById("fetchReportBtn");
  const monthlyTotalEl    = document.getElementById("monthlyTotal");
  const monthlyCountEl    = document.getElementById("monthlyCount");

  // Export
  const exportThisMonthBtn   = document.getElementById("exportThisMonthBtn");
  const exportStartDateInput = document.getElementById("exportStartDate");
  const exportEndDateInput   = document.getElementById("exportEndDate");
  const exportExcelBtn       = document.getElementById("exportExcelBtn");
  const exportStatusEl       = document.getElementById("exportStatus");

  // ── INIT ─────────────────────────────────────────────────
  initApp();

  async function initApp() {
    setupEventListeners();
    if (API.isAuthenticated()) {
      await loadUserData();
    } else {
      showAuthScreen();
    }
  }

  // ── EVENT LISTENERS ───────────────────────────────────────
  function setupEventListeners() {
    loginTab?.addEventListener("click",    () => setAuthMode("login"));
    registerTab?.addEventListener("click", () => setAuthMode("register"));
    authForm?.addEventListener("submit",   handleAuthSubmit);
    otpForm?.addEventListener("submit",    handleOtpSubmit);
    resendOtpBtn?.addEventListener("click", handleResendOtp);

    backToLoginFromOtp?.addEventListener("click", (e) => { e.preventDefault(); showAuthFormView(); });
    forgotPasswordLink?.addEventListener("click",  (e) => { e.preventDefault(); showForgotFormView(); });
    backToLoginFromForgot?.addEventListener("click", (e) => { e.preventDefault(); showAuthFormView(); });
    sendResetOtpBtn?.addEventListener("click",        handleSendResetOtp);
    submitResetPasswordBtn?.addEventListener("click", handleSubmitResetPassword);

    logoutBtn?.addEventListener("click", handleLogout);

    // Tx modal
    openAddTxBtn?.addEventListener("click", () => openModal(txModal));
    closeTxModal?.addEventListener("click",  () => closeModal(txModal));
    txForm?.addEventListener("submit",        handleCreateTransaction);

    // Detail modal
    closeTxDetailModal?.addEventListener("click", () => closeModal(txDetailModal));

    // Date range modal
    openDateRangeModalBtn?.addEventListener("click", () => { fillDefaultDateRange(); openModal(dateRangeModal); });
    closeDateRangeModal?.addEventListener("click",   () => closeModal(dateRangeModal));
    applyDateRangeBtn?.addEventListener("click",      handleAnalyzeDateRange);

    // Settings modal
    openSettingsBtn?.addEventListener("click", () => {
      if (currentUser) {
        document.getElementById("updateName").value  = currentUser.name  || "";
        document.getElementById("updateEmail").value = currentUser.email || "";
      }
      openModal(settingsModal);
    });
    closeSettingsModal?.addEventListener("click", () => closeModal(settingsModal));
    settingsForm?.addEventListener("submit",       handleUpdateSettings);
    deleteAccountBtn?.addEventListener("click",    handleDeleteAccount);

    // Pagination
    prevPageBtn?.addEventListener("click", () => { if (currentPage > 1) { currentPage--; loadTransactions(); } });
    nextPageBtn?.addEventListener("click", () => { currentPage++; loadTransactions(); });
    pageSizeSelect?.addEventListener("change", (e) => { pageSize = parseInt(e.target.value); currentPage = 1; loadTransactions(); });

    // Sort
    sortSelect?.addEventListener("change", (e) => {
      const [by, order] = e.target.value.split("-");
      currentSortBy = by; currentSortOrder = order;
      loadSortedTransactions();
    });

    // Search
    searchInput?.addEventListener("input", (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        const q = e.target.value.trim();
        q.length > 0 ? performSearch(q) : loadTransactions();
      }, 350);
    });

    // Reports & export
    fetchReportBtn?.addEventListener("click",     loadMonthlyReport);
    exportThisMonthBtn?.addEventListener("click", fillExportCurrentMonth);
    exportExcelBtn?.addEventListener("click",     handleDownloadExcel);

    window.addEventListener("auth:unauthorized", () => {
      showToast("Session expired. Please log in.", "error");
      showAuthScreen();
    });
  }

  // ══════════════════════════════════════════
  // AUTH VIEW MANAGEMENT
  // ══════════════════════════════════════════
  function setAuthMode(mode) {
    authMode = mode;
    showAuthFormView();
    if (mode === "login") {
      loginTab?.classList.add("active");
      registerTab?.classList.remove("active");
      nameGroup?.classList.add("hidden");
      if (authTitle) authTitle.innerText = "Welcome back";
      if (authBtnText) authBtnText.innerText = "Sign In";
    } else {
      registerTab?.classList.add("active");
      loginTab?.classList.remove("active");
      nameGroup?.classList.remove("hidden");
      if (authTitle) authTitle.innerText = "Create your account";
      if (authBtnText) authBtnText.innerText = "Create Account";
    }
  }

  function showAuthFormView() {
    // Show the login/register form
    authForm?.classList.remove("hidden");
    authTabs?.classList.remove("hidden");
    // Hide OTP and forgot screens
    otpScreen?.classList.add("hidden");
    forgotScreen?.classList.add("hidden");
    // Hide step indicator
    stepIndicator?.classList.add("hidden");
    // Reset step indicator states
    setStep(1);
    if (resendCountdownInterval) clearInterval(resendCountdownInterval);
  }

  function showOtpVerificationView(email) {
    pendingVerificationEmail = email;
    if (otpTargetEmail) otpTargetEmail.innerText = email;
    if (otpInput) otpInput.value = "";

    // Hide login form & tabs
    authForm?.classList.add("hidden");
    authTabs?.classList.add("hidden");
    forgotScreen?.classList.add("hidden");

    // Show step indicator at step 2
    stepIndicator?.classList.remove("hidden");
    setStep(2);

    // Show OTP screen
    otpScreen?.classList.remove("hidden");
    if (authTitle) authTitle.innerText = "Verify your email";
    startResendTimer(30);
  }

  function showForgotFormView() {
    authForm?.classList.add("hidden");
    authTabs?.classList.add("hidden");
    otpScreen?.classList.add("hidden");
    stepIndicator?.classList.add("hidden");
    forgotScreen?.classList.remove("hidden");
    forgotStep1?.classList.remove("hidden");
    forgotStep2?.classList.add("hidden");
    if (authTitle) authTitle.innerText = "Reset password";
  }

  // Step indicator helper
  function setStep(step) {
    // Reset all
    [step1Item, step2Item, step3Item].forEach(el => {
      el?.classList.remove("active", "done");
    });
    const lines = document.querySelectorAll(".step-line");

    if (step === 1) {
      step1Item?.classList.add("active");
    } else if (step === 2) {
      step1Item?.classList.add("done");
      step2Item?.classList.add("active");
      if (lines[0]) lines[0].classList.add("done");
    } else if (step === 3) {
      step1Item?.classList.add("done");
      step2Item?.classList.add("done");
      step3Item?.classList.add("active");
      lines.forEach(l => l.classList.add("done"));
    }
  }

  // ── Auth Handlers ─────────────────────────────────────────
  async function handleAuthSubmit(e) {
    e.preventDefault();
    const email    = document.getElementById("authEmail").value.trim();
    const password = document.getElementById("authPassword").value;

    try {
      if (authMode === "login") {
        await API.login(email, password);
        showToast("Welcome back!", "success");
        await loadUserData();
      } else {
        const name = document.getElementById("authName").value.trim();
        const res  = await API.register(name, email, password);
        showToast(res.message || "Account created! Check your email for the verification code.", "success");
        showOtpVerificationView(email);
      }
    } catch (err) {
      if (err.message?.toLowerCase().includes("not verified")) {
        showToast("Please verify your email first.", "error");
        showOtpVerificationView(email);
      } else {
        showToast(err.message, "error");
      }
    }
  }

  async function handleOtpSubmit(e) {
    e.preventDefault();
    const otp = otpInput?.value.trim();
    if (!otp || otp.length !== 6) {
      showToast("Enter a valid 6-digit code.", "error");
      return;
    }
    try {
      const res = await API.verifyOTP(pendingVerificationEmail, otp);
      // Show step 3 (done) briefly before transitioning
      setStep(3);
      showToast(res.message || "Email verified! Welcome 🎉", "success");
      setTimeout(async () => {
        stepIndicator?.classList.add("hidden");
        await loadUserData();
      }, 700);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function handleResendOtp() {
    if (!pendingVerificationEmail) return;
    try {
      const res = await API.resendOTP(pendingVerificationEmail);
      showToast(res.message || "New code sent to your email.", "success");
      startResendTimer(30);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  function startResendTimer(seconds = 30) {
    if (!resendOtpBtn || !resendTimer) return;
    resendOtpBtn.disabled = true;
    let remaining = seconds;
    resendTimer.innerText = `(${remaining}s)`;
    if (resendCountdownInterval) clearInterval(resendCountdownInterval);
    resendCountdownInterval = setInterval(() => {
      remaining--;
      if (remaining <= 0) {
        clearInterval(resendCountdownInterval);
        resendOtpBtn.disabled = false;
        resendTimer.innerText = "";
      } else {
        resendTimer.innerText = `(${remaining}s)`;
      }
    }, 1000);
  }

  async function handleSendResetOtp() {
    const email = forgotEmailInput?.value.trim();
    if (!email) { showToast("Enter your email address.", "error"); return; }
    try {
      const res = await API.forgotPassword(email);
      showToast(res.message || "Reset code sent to your email.", "success");
      forgotStep1?.classList.add("hidden");
      forgotStep2?.classList.remove("hidden");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function handleSubmitResetPassword() {
    const email       = forgotEmailInput?.value.trim();
    const otp         = resetOtpInput?.value.trim();
    const newPassword = newPasswordInput?.value;
    if (!otp || !newPassword) { showToast("Fill in both code and new password.", "error"); return; }
    try {
      const res = await API.resetPassword(email, otp, newPassword);
      showToast(res.message || "Password updated! Please sign in.", "success");
      showAuthFormView();
      setAuthMode("login");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  function handleLogout() {
    API.removeToken();
    currentUser = null;
    showToast("Signed out.", "success");
    showAuthScreen();
  }

  function showAuthScreen() {
    authSection?.classList.remove("hidden");
    mainAppSection?.classList.add("hidden");
    showAuthFormView();
  }

  function showMainAppScreen() {
    authSection?.classList.add("hidden");
    mainAppSection?.classList.remove("hidden");
  }

  // ══════════════════════════════════════════
  // DATA LOADING — All Router Integrations
  // ══════════════════════════════════════════
  async function loadUserData() {
    try {
      currentUser = await API.getMe();
      renderUserProfile();
      showMainAppScreen();
      await Promise.all([
        loadDashboardStats(),
        loadTransactions(),
        loadSpendAnalytics(),
        loadMonthlyReport()
      ]);
    } catch (err) {
      console.error(err);
      showAuthScreen();
    }
  }

  function renderUserProfile() {
    if (!currentUser) return;
    if (userNameEl)   userNameEl.innerText  = currentUser.name  || "User";
    if (userEmailEl)  userEmailEl.innerText = currentUser.email || "";
    if (userAvatarEl) userAvatarEl.innerText = (currentUser.name || currentUser.email || "U").substring(0, 2).toUpperCase();
  }

  // 1. /dashboard/
  async function loadDashboardStats() {
    try {
      const s = await API.getDashboard();
      if (totalBalanceEl)   totalBalanceEl.innerText  = formatCurrency(s.balance || 0);
      if (totalIncomeEl)    totalIncomeEl.innerText   = formatCurrency(s.income  || 0);
      if (totalExpenseEl)   totalExpenseEl.innerText  = formatCurrency(s.expense || 0);
      if (highestExpenseEl) highestExpenseEl.innerText = s.highest_expense ? formatCurrency(s.highest_expense) : "₹0.00";
      if (lowestExpenseEl)  lowestExpenseEl.innerText  = s.lowest_expense  ? formatCurrency(s.lowest_expense)  : "₹0.00";
      if (totalTxCountEl)   totalTxCountEl.innerText  = s["total transaction"] || 0;
    } catch (err) { console.error("Dashboard:", err); }
  }

  // 2. /report/spends
  async function loadSpendAnalytics() {
    try {
      const spend = await API.getSpendReport();
      const income  = spend.Income  || spend.income  || 0;
      const expense = spend.Expense || spend.expense || 0;
      const total   = income + expense;
      if (spendIncomeLabel)  spendIncomeLabel.innerText  = formatCurrency(income);
      if (spendExpenseLabel) spendExpenseLabel.innerText = formatCurrency(expense);
      const ratio = total > 0 ? (expense / total) * 100 : 0;
      if (spendProgressBar)  spendProgressBar.style.width  = `${Math.min(100, Math.max(0, ratio))}%`;
      if (spendRatioPercent) spendRatioPercent.innerText   = `${Math.round(ratio)}% spent`;
    } catch (err) { console.error("Spend analytics:", err); }
  }

  // 3. /pagination/
  async function loadTransactions() {
    try {
      let transactions = [];
      try {
        transactions = await API.getPaginatedTransactions(currentPage, pageSize);
      } catch {
        const allTx = await API.getTransactions();
        transactions = Array.isArray(allTx) ? allTx : [];
      }
      renderTransactionTable(transactions);
      if (currentPageBadge) currentPageBadge.innerText = `Page ${currentPage}`;
      if (prevPageBtn) prevPageBtn.disabled = currentPage <= 1;
      if (nextPageBtn) nextPageBtn.disabled = transactions.length < pageSize;
    } catch (err) { console.error("Transactions:", err); }
  }

  // 4. /report/sortby
  async function loadSortedTransactions() {
    try {
      const sorted = await API.getSortedTransactions(currentSortBy, currentSortOrder);
      renderTransactionTable(sorted || []);
      if (currentPageBadge) currentPageBadge.innerText = "Sorted";
      if (prevPageBtn) prevPageBtn.disabled = true;
      if (nextPageBtn) nextPageBtn.disabled = true;
    } catch (err) { console.error("Sort:", err); }
  }

  // 5. /pagination/search
  async function performSearch(query) {
    try {
      const results = await API.searchTransactions(query);
      renderTransactionTable(results || []);
      if (currentPageBadge) currentPageBadge.innerText = "Search";
      if (prevPageBtn) prevPageBtn.disabled = true;
      if (nextPageBtn) nextPageBtn.disabled = true;
    } catch (err) { console.error("Search:", err); }
  }

  function renderTransactionTable(transactions) {
    if (!transactionsTableBody) return;
    transactionsTableBody.innerHTML = "";

    if (!transactions || transactions.length === 0) {
      transactionsTableBody.innerHTML = `
        <tr><td colspan="6" class="empty-cell">
          No transactions found. Click <strong>+ New</strong> to add one.
        </td></tr>
      `;
      return;
    }

    transactions.forEach((tx) => {
      const isIncome  = (tx.type || "").toLowerCase() === "income";
      const color     = isIncome ? "var(--income)" : "var(--expense)";
      const prefix    = isIncome ? "+" : "−";
      const badgeCls  = isIncome ? "badge-income" : "badge-expense";
      const row = document.createElement("tr");

      row.innerHTML = `
        <td style="font-weight:600;cursor:pointer;color:var(--amber)" class="tx-name-click" data-name="${escapeHtml(tx.name || '')}">
          ${escapeHtml(tx.name || "—")}
        </td>
        <td><span class="badge ${badgeCls}">${tx.type || "expense"}</span></td>
        <td style="color:var(--txt-2);font-size:0.83rem">${escapeHtml(tx.description || "—")}</td>
        <td style="font-weight:700;color:${color}">${prefix}${formatCurrency(tx.amount || 0)}</td>
        <td style="color:var(--txt-3);font-size:0.8rem">${tx.date ? new Date(tx.date).toLocaleDateString() : "—"}</td>
        <td class="col-right">
          <button class="btn-inspect" data-name="${escapeHtml(tx.name || '')}">Inspect</button>
        </td>
      `;

      row.querySelector(".tx-name-click")?.addEventListener("click", () => inspectTransaction(tx.name));
      row.querySelector(".btn-inspect")?.addEventListener("click",   () => inspectTransaction(tx.name));
      transactionsTableBody.appendChild(row);
    });
  }

  // 6. /transaction/{name}
  async function inspectTransaction(name) {
    if (!name) return;
    try {
      const tx = await API.getTransactionByName(name);
      if (!tx) return;
      const isIncome = (tx.type || "").toLowerCase() === "income";
      txDetailContent.innerHTML = `
        <div class="detail-row"><span class="detail-lbl">Title</span><span class="detail-val" style="color:var(--amber)">${escapeHtml(tx.name)}</span></div>
        <div class="detail-row"><span class="detail-lbl">Type</span><span class="badge ${isIncome ? 'badge-income' : 'badge-expense'}">${tx.type}</span></div>
        <div class="detail-row"><span class="detail-lbl">Amount</span><span class="detail-val" style="color:${isIncome ? 'var(--income)' : 'var(--expense)'}">${formatCurrency(tx.amount || 0)}</span></div>
        <div class="detail-row"><span class="detail-lbl">Description</span><span class="detail-val">${escapeHtml(tx.description || "N/A")}</span></div>
        <div class="detail-row"><span class="detail-lbl">ID</span><span class="detail-val" style="font-size:0.8rem;color:var(--txt-2)">${tx.id || "N/A"}</span></div>
        <div class="detail-row"><span class="detail-lbl">Date</span><span class="detail-val">${tx.date ? new Date(tx.date).toLocaleString() : "N/A"}</span></div>
      `;
      openModal(txDetailModal);
    } catch (err) { showToast(err.message, "error"); }
  }

  // 7. POST /transaction/
  async function handleCreateTransaction(e) {
    e.preventDefault();
    const name        = document.getElementById("txName").value.trim();
    const type        = document.getElementById("txType").value;
    const amount      = parseFloat(document.getElementById("txAmount").value);
    const description = document.getElementById("txDescription").value.trim();
    try {
      await API.createTransaction({ name, type, amount, description });
      showToast("Transaction saved!", "success");
      closeModal(txModal);
      txForm.reset();
      await Promise.all([loadDashboardStats(), loadTransactions(), loadSpendAnalytics(), loadMonthlyReport()]);
    } catch (err) { showToast(err.message, "error"); }
  }

  // 8. PUT /update-user/profile
  async function handleUpdateSettings(e) {
    e.preventDefault();
    const name     = document.getElementById("updateName").value.trim();
    const email    = document.getElementById("updateEmail").value.trim();
    const password = document.getElementById("updatePassword").value;
    try {
      await API.updateUser(name, email, password);
      showToast("Profile updated!", "success");
      closeModal(settingsModal);
      await loadUserData();
    } catch (err) { showToast(err.message, "error"); }
  }

  // 9. DELETE /auth/delete-users
  async function handleDeleteAccount() {
    if (!currentUser?.email) return;
    const confirmed = confirm(`Delete account "${currentUser.email}" and ALL transactions? This cannot be undone.`);
    if (!confirmed) return;
    try {
      await API.deleteUser(currentUser.email);
      showToast("Account deleted.", "success");
      closeModal(settingsModal);
      handleLogout();
    } catch (err) { showToast(err.message, "error"); }
  }

  // 10. /report/date_range & /report/amount_total
  function fillDefaultDateRange() {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, "0");
    if (drStartDate) drStartDate.value = `${y}-${m}-01`;
    const last = new Date(y, now.getMonth() + 1, 0).getDate();
    if (drEndDate)   drEndDate.value   = `${y}-${m}-${String(last).padStart(2, "0")}`;
  }

  async function handleAnalyzeDateRange() {
    const start = drStartDate?.value;
    const end   = drEndDate?.value;
    const type  = drType?.value;
    if (!start || !end) { showToast("Select both dates.", "error"); return; }
    try {
      const summary = await API.getAmountTotal(start, end, type);
      const min  = summary["min amount"] ?? 0;
      const max  = summary["max amount"] ?? 0;
      const list = summary.transaction  || [];
      if (drMinAmount) drMinAmount.innerText = formatCurrency(min);
      if (drMaxAmount) drMaxAmount.innerText = formatCurrency(max);
      if (drCount)     drCount.innerText     = list.length;
      if (drResultsBody) {
        drResultsBody.innerHTML = "";
        if (list.length === 0) {
          drResultsBody.innerHTML = `<tr><td colspan="4" class="empty-cell">No transactions in this range.</td></tr>`;
        } else {
          list.forEach(tx => {
            const isIn = (tx.type || "").toLowerCase() === "income";
            const row  = document.createElement("tr");
            row.innerHTML = `
              <td style="font-weight:600">${escapeHtml(tx.name)}</td>
              <td><span class="badge ${isIn ? 'badge-income' : 'badge-expense'}">${tx.type}</span></td>
              <td style="font-weight:700;color:${isIn ? 'var(--income)' : 'var(--expense)'}">${formatCurrency(tx.amount || 0)}</td>
              <td style="color:var(--txt-3);font-size:0.8rem">${tx.date ? new Date(tx.date).toLocaleDateString() : "—"}</td>
            `;
            drResultsBody.appendChild(row);
          });
        }
      }
    } catch (err) { showToast(err.message, "error"); }
  }

  // 11. /report/monthly
  async function loadMonthlyReport() {
    const now   = new Date();
    const month = parseInt(reportMonthInput?.value || now.getMonth() + 1);
    const year  = parseInt(reportYearInput?.value  || now.getFullYear());
    const type  = reportTypeFilter?.value || "";
    try {
      const res = await API.getMonthlyReport(month, year, type);
      if (monthlyTotalEl) monthlyTotalEl.innerText = formatCurrency(res.total || 0);
      if (monthlyCountEl) monthlyCountEl.innerText = res["total transaction count"] || 0;
    } catch (err) { console.error("Monthly report:", err); }
  }

  // 12. /report-downlaod/export-monthly
  function fillExportCurrentMonth() {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, "0");
    const first = `${y}-${m}-01`;
    const last  = `${y}-${m}-${String(new Date(y, now.getMonth() + 1, 0).getDate()).padStart(2, "0")}`;
    if (exportStartDateInput) exportStartDateInput.value = first;
    if (exportEndDateInput)   exportEndDateInput.value   = last;
    if (exportStatusEl)       exportStatusEl.innerText   = `Preset: ${first} → ${last}`;
  }

  async function handleDownloadExcel() {
    const start = exportStartDateInput?.value;
    const end   = exportEndDateInput?.value;
    if (!start || !end) { showToast("Select both dates.", "error"); return; }
    try {
      if (exportStatusEl) exportStatusEl.innerText = "Generating…";
      if (exportExcelBtn) exportExcelBtn.disabled  = true;
      const blob = await API.downloadMonthlyExcel(start, end);
      const url  = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `transactions_${start}_to_${end}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      if (exportStatusEl) exportStatusEl.innerText = "Downloaded ✓";
      showToast("Report downloaded!", "success");
    } catch (err) {
      if (exportStatusEl) exportStatusEl.innerText = "Download failed.";
      showToast(err.message, "error");
    } finally {
      if (exportExcelBtn) exportExcelBtn.disabled = false;
    }
  }

  // ── Modal helpers ─────────────────────────────────────────
  function openModal(el)  { if (el) el.classList.add("active"); }
  function closeModal(el) { if (el) el.classList.remove("active"); }

  // ── Toast ─────────────────────────────────────────────────
  function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const icon = type === "success" ? "✓" : "!";
    toast.innerHTML = `<span class="toast-icon">${icon}</span><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.transition = "opacity 0.28s, transform 0.28s";
      toast.style.opacity    = "0";
      toast.style.transform  = "translateX(110%)";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // ── Helpers ───────────────────────────────────────────────
  function formatCurrency(val) {
    return new Intl.NumberFormat("en-IN", {
      style: "currency", currency: "INR", maximumFractionDigits: 2
    }).format(val);
  }

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
});
