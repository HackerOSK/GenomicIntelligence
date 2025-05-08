/**
 * JavaScript for handling report processing functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Load sample report button
    const loadSampleButton = document.getElementById('loadSampleReport');
    if (loadSampleButton) {
        loadSampleButton.addEventListener('click', loadSampleReport);
    }
});

/**
 * Load a sample pathology report for demonstration purposes
 */
function loadSampleReport() {
    const reportTextarea = document.getElementById('report_text');
    if (!reportTextarea) return;
    
    const sampleReport = `LABORATORY REPORT
Date: 2023-06-15
Patient ID: P12345
------------------------------------------

COMPLETE BLOOD COUNT (CBC)
WBC: 7.2 x 10^3/µL (Normal: 4.5-11.0)
RBC: 4.8 x 10^6/µL (Normal: 4.2-5.4)
Hemoglobin: 14.2 g/dL (Normal: 12.0-16.0)
Hematocrit: 42% (Normal: 36-46%)
Platelets: 250 x 10^3/µL (Normal: 150-450)

COMPREHENSIVE METABOLIC PANEL
Glucose: 105 mg/dL (Normal: 70-99) - Slightly Elevated
BUN: 15 mg/dL (Normal: 7-20)
Creatinine: 0.9 mg/dL (Normal: 0.6-1.2)
eGFR: >90 mL/min/1.73m² (Normal: >60)
TSH: 3.2 mIU/L (Normal: 0.4-4.0)
T3: 120 ng/dL (Normal: 80-200)

LIPID PROFILE
Total Cholesterol: 210 mg/dL (Normal: <200) - Elevated
LDL: 140 mg/dL (Normal: <100) - Elevated
HDL: 45 mg/dL (Normal: >40)
Triglycerides: 150 mg/dL (Normal: <150)

GENETIC ANALYSIS
BRCA1: Negative for pathogenic variants
EGFR: Detected T790M mutation
TP53: Wild type

DIAGNOSIS
1. Hypercholesterolemia
2. Impaired Fasting Glucose
3. EGFR mutation positive

NOTES
Patient reports occasional headaches and fatigue. Currently taking aspirin 81mg daily. Previous history of hypertension, well-controlled with diet and exercise. Recommend monitoring blood glucose and cholesterol levels.

------------------------------------------
Dr. Sarah Johnson, MD
Clinical Pathologist
License #: MD12345
`;
    
    reportTextarea.value = sampleReport;
    
    // Show notification
    showNotification('Sample report loaded successfully!', 'success');
}

/**
 * Submit report form programmatically
 */
function submitReportForm() {
    const reportForm = document.querySelector('#report_text').closest('form');
    if (reportForm) {
        reportForm.submit();
    }
}

/**
 * Preview extraction results before submission
 * Note: In a full implementation, this would make an AJAX call to the backend
 */
function previewExtraction() {
    const reportText = document.getElementById('report_text').value;
    if (!reportText) {
        showNotification('Please enter report text first', 'warning');
        return;
    }
    
    // Simulate loading state
    showNotification('Analyzing report...', 'info');
    
    // In a real implementation, this would call the API endpoint
    // For demo, we'll just simulate the delay
    setTimeout(() => {
        showNotification('Analysis complete! Submit the form to continue.', 'success');
    }, 1500);
}
