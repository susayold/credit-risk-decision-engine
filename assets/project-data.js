window.PORTFOLIO_PROJECTS = {
  "3": {
    number: "03",
    status: "Closed - recruiter ready",
    statusClass: "complete",
    accent: "#0d6b67",
    category: "Credit Risk Modeling",
    title: "Credit Risk Decision Engine",
    thesis: "A formula-first credit scorecard project that moves from matured target definition through WOE/IV, PD, scorecard points, out-of-time validation, cutoff economics and model governance.",
    tags: ["Credit scorecard", "WOE/IV", "PD", "Logistic regression", "AUC/KS", "Calibration", "Cutoff", "Model governance"],
    metrics: [
      { value: "1.348M", label: "Core booked accounts" },
      { value: "0.781", label: "Clean WOE-logistic test AUC" },
      { value: "0.418", label: "Clean scorecard test KS" },
      { value: "0.793", label: "Raw logistic challenger AUC" },
      { value: "100K", label: "Portable reviewer sample" }
    ],
    business: {
      question: "Which lending accounts are most likely to default, why are they risky, what cutoff balances approval and expected loss, and what evidence is required before production use?",
      context: "A credit score is useful only when its population, target, ranking, calibration, policy trade-offs and limitations are transparent to Risk, Business and Model Governance.",
      output: "A layered scorecard stack, cutoff simulator, expected-loss view, model card, validation evidence, governance logs and a lightweight reviewer mode."
    },
    dataLayers: [
      { meta: "Portfolio foundation", title: "1.35M accepted/booked accounts", text: "Thin/core features support maturity, target, baseline PD, EL, cutoff, monitoring and concentration." },
      { meta: "Enriched modeling", title: "331,865 accepted loans", text: "Seventeen application-time candidate features support WOE fitting, a clean WOE-logistic scorecard and a raw logistic challenger." },
      { meta: "Selection-bias context", title: "27.65M rejected applications", text: "Used for reject-inference sensitivity and funnel context only because repayment outcomes are unobserved." },
      { meta: "Reference extension", title: "SBA charge-off evidence", text: "Used as separate SME recovery/concentration reference and never merged into the consumer scorecard target." }
    ],
    formulas: [
      { name: "Weight of Evidence", expression: "WOE_bin = ln(Dist_good / Dist_bad)", meaning: "Encodes each bin by its relative concentration of good and bad accounts under the project convention.", use: "Explainable risk ordering and scorecard input." },
      { name: "Information Value", expression: "IV = SUM((Dist_good - Dist_bad) x WOE_bin)", meaning: "Measures univariate separation of each candidate variable.", use: "Driver screening, not automatic feature approval." },
      { name: "Formula risk score", expression: "Risk Score Raw = -SUM(IV_weight_variable x WOE_bin)", meaning: "Combines transparent WOE evidence; higher raw score means higher risk.", use: "Formula-first segmentation benchmark." },
      { name: "Scorecard points", expression: "Score = Offset + (PDO / ln(2)) x ln((1 - PD) / PD)", meaning: "Transforms default odds into familiar scorecard points using base score 600, good odds 20 and PDO 50.", use: "Policy-friendly communication." },
      { name: "Expected loss", expression: "EL = PD x LGD x EAD", meaning: "Connects model risk ranking to monetary impact.", use: "Cutoff, concentration and portfolio economics." }
    ],
    process: [
      { title: "Define the decision population", text: "Separate application, accepted/booked, matured, monitor-only and rejected populations; set a 12-month performance window.", evidence: "1,291,521 matured accounts" },
      { title: "Create the good/bad target", text: "Label matured defaults as bad, matured non-defaults as good and under-seasoned accounts as indeterminate.", evidence: "20.16% matured bad rate" },
      { title: "Build transparent WOE/IV evidence", text: "Bin drivers, smooth sparse categories, review monotonicity, missingness, IV strength and potential proxy concerns.", evidence: "Training-window-only WOE fitting" },
      { title: "Build the model stack", text: "Compare thin formula baseline, expanded IV-weighted formula, final clean WOE-logistic scorecard and raw logistic challenger.", evidence: "Out-of-time 2016/2017 splits" },
      { title: "Validate ranking and calibration", text: "Measure AUC, Gini, KS, Brier, decile calibration, high-risk tail gap, stability and term sensitivity.", evidence: "Clean scorecard test AUC 0.781" },
      { title: "Simulate policy cutoffs", text: "Quantify approval rate, approved bad rate, bad capture, EAD and expected loss across PD cutoffs.", evidence: "15%, 20%, 25% and sensitivity grid" },
      { title: "Govern the recommendation", text: "Separate benchmark, conditional candidate and production model; document exclusions, fairness/proxy review and recalibration limits.", evidence: "No final production model selected" }
    ],
    resultTables: [
      {
        title: "Out-of-time model stack",
        note: "The 1.3M thin baseline and 331.9K enriched models are different populations and are not presented as a same-population uplift test.",
        headers: ["Layer", "Population", "Test AUC", "Test KS", "Decision"],
        rows: [
          ["Thin baseline", "1.3M portfolio base", "0.626", "0.180", "Keep for target, EL, cutoff and monitoring"],
          ["Expanded WOE formula", "331.9K enriched", "0.765", "0.400", "Explainability benchmark"],
          ["Clean WOE-logistic", "331.9K enriched", "0.781", "0.418", "Conditional portfolio candidate"],
          ["Raw logistic challenger", "331.9K enriched", "0.793", "0.440", "Performance benchmark only"]
        ]
      },
      {
        title: "Cutoff economics on matured portfolio",
        note: "A tighter cutoff improves risk outcomes but reduces approvals and shifts substantial volume to review/non-approved queues.",
        headers: ["PD cutoff", "Approval", "Approved bad rate", "Bad capture outside approval", "Approved EL"],
        rows: [
          ["15%", "29.44%", "12.13%", "82.30%", "252.3M"],
          ["20%", "49.47%", "14.64%", "64.07%", "511.3M"],
          ["25%", "79.79%", "17.64%", "30.20%", "1.022B"],
          ["35%", "100.00%", "20.16%", "0.00%", "1.473B"]
        ]
      },
      {
        title: "Calibration evidence",
        note: "Average calibration is not enough; tail underprediction matters because high-risk deciles drive cutoff, pricing and EL decisions.",
        headers: ["Model", "Test calibration gap", "Tail finding"],
        rows: [
          ["Thin baseline", "+3.50 pp", "Decile PD mapping is mechanical; out-of-time gap is the real check"],
          ["Expanded WOE formula", "+1.62 pp", "Transparent but still underpredicts later outcomes"],
          ["Clean WOE-logistic", "+1.81 pp", "Conditional candidate; tail review remains required"],
          ["Raw logistic", "+1.44 pp", "Best average gap; governance readiness remains lower"],
          ["High-risk decile 10", "+6.92 pp pre-recalibration", "Diagnostic recalibration only; no production PD selected"]
        ]
      }
    ],
    alerts: [
      { tone: "amber", text: "Thin baseline AUC 0.626 is moderate ranking power, not a strong production underwriting model." },
      { tone: "red", text: "High-risk tail underprediction must be recalibrated and independently validated before pricing, ECL or automated cutoff use." },
      { tone: "info", text: "The clean WOE-logistic scorecard is a conditional portfolio demonstration candidate; the final production model is explicitly not selected." },
      { tone: "info", text: "Rejected applications support sensitivity analysis only because their repayment outcomes are not observed." }
    ],
    decision: {
      finding: "The clean WOE-logistic scorecard materially improves ranking over the thin formula baseline while retaining scorecard explainability. The raw logistic challenger performs best, but its extra performance does not remove calibration, stability and governance requirements.",
      recommendation: "Use the clean scorecard for portfolio demonstration and controlled policy analysis. Do not deploy automated underwriting without internal data, approved recalibration, fairness/proxy review and independent validation."
    },
    charts: [
      { src: "assets/images/p3-challenger-comparison.png", alt: "AUC and KS comparison across credit risk model layers", caption: "Model stack: ranking improves as richer application-time evidence is added." },
      { src: "assets/images/p3-cutoff-tradeoff.png", alt: "Credit policy cutoff approval and bad-rate trade-off", caption: "Cutoff trade-off: lower PD thresholds reduce approved risk but sharply reduce approval volume." },
      { src: "assets/images/p3-calibration.png", alt: "Logistic scorecard calibration curve", caption: "Calibration review: average fit and high-risk-tail behavior are evaluated separately." },
      { src: "assets/images/p3-vintage.png", alt: "Observed default rate by vintage", caption: "Vintage evidence: portfolio performance is monitored across origination cohorts." }
    ],
    validation: {
      headline: "Public package and portable reviewer path passed the final project controls.",
      cards: [
        { title: "Performance", text: "Time-aware train, 2016 validation and 2017 test windows preserve out-of-time evidence." },
        { title: "Leakage", text: "Pricing-derived sub-grade and interest rate are excluded from model features." },
        { title: "Stability", text: "Sparse-bin cleanup, sign review, CSI/PSI, term sensitivity and tail diagnostics are documented." },
        { title: "Portability", text: "100k samples support reviewer inspection; required-file and ZIP path checks passed." }
      ]
    },
    limitations: [
      "This is a formula-first educational credit-risk project, not a production automated underwriting model.",
      "Baseline and enriched results use different populations and must not be read as a single controlled model uplift.",
      "Formula PD in the thin layer is mapped from observed decile bad rates; out-of-time validation is the meaningful calibration check.",
      "Reject outcomes, consumer workout recoveries, observed overrides and monthly delinquency transitions are unavailable.",
      "Independent validation, approved calibration, adverse-action review and production governance have not been performed."
    ],
    employerValues: [
      { title: "Model judgment", text: "I can distinguish target design, score construction, ranking, calibration and policy use." },
      { title: "Business trade-offs", text: "I can translate a PD distribution into approval, bad capture and expected-loss choices." },
      { title: "Governance discipline", text: "I can document exclusions, challengers, tail risk, limitations and production gates without overclaiming." }
    ],
    artifacts: [
      { label: "Open complete FINAL package", type: "HTML", href: "OPEN_THIS_FIRST.html", detail: "Original reports, scripts, data, models and validation evidence" },
      { label: "Project 3 README", type: "MD", href: "evidence/project-3/README.md", detail: "Full methodology, results and positioning" },
      { label: "Model card", type: "MD", href: "evidence/project-3/model_card.md", detail: "Population, performance and governance" },
      { label: "Validation metrics", type: "CSV", href: "evidence/project-3/validation_metrics.csv", detail: "Baseline performance evidence" },
      { label: "Cutoff strategy", type: "CSV", href: "evidence/project-3/cutoff_strategy.csv", detail: "Approval and loss trade-offs" },
      { label: "Final model recommendation", type: "CSV", href: "evidence/project-3/final_model_recommendation.csv", detail: "Keep, candidate and benchmark decisions" }
    ],
    next: { href: "#artifacts", label: "Evidence pack", title: "Supporting artifacts" }
  }
};
