# Script Doctor - UAT Round 2

## Overview

This directory contains all materials related to User Acceptance Testing (UAT) Round 2 for the Script Doctor application. Round 2 is focused on validating the effectiveness of the remediation efforts implemented based on feedback from UAT Round 1.

## Key Issues Being Validated

1. **UI/UX Improvements**: Simplified single text area design replacing the confusing dual text area approach
2. **Beat Definition Accuracy**: Resolved confusion between similar beat types (especially All Is Lost vs Dark Night of the Soul)
3. **Analysis Quality**: Improved relevance, specificity, and actionability of feedback
4. **Technical Improvements**: Fixed API model naming, error handling, and collection management

## Documents

### Preparation Materials

- [Preparation Checklist](preparation_checklist.md): Checklist for UAT Round 2 preparation
- [Key Fixes](key_fixes.md): Summary of the remediation efforts being validated
- [Recreation Plan](recreation_plan.md): Plan for recreating the key UAT documents

### Testing Materials

- [Instructions](uat_round2_instructions.md): Main instructions document for testers
- [Test Guide](test_guide.md): Step-by-step instructions for each test case
- [Feedback Form](feedback_form.md): Form for testers to document their observations

### Administration Materials

- [Tester Assignments](tester_assignments.md): Assignment of test cases to testers
- [Results Tracker](results_tracker.md): Document for tracking and aggregating test results

## Test Data

The test data is located in the `data/uat_samples/` directory:

- `well_structured_outline.txt`: A complete outline following Save the Cat principles closely
- `partially_structured_outline.txt`: An outline with some beats implemented well, others missing or weak
- `problematic_outline.txt`: An outline with intentional structural issues and missing setups

## Test Cases

| Test Case ID | Description | Focus Area |
|--------------|-------------|------------|
| TC-R2-01 | Basic UI Workflow | UI/UX |
| TC-R2-02 | Visual Feedback Validation | UI/UX |
| TC-R2-03 | All Is Lost Beat Definition | Beat Definition |
| TC-R2-04 | Dark Night of the Soul Beat Definition | Beat Definition |
| TC-R2-05 | Well-Defined Beat (Midpoint) | Beat Definition |
| TC-R2-06 | All Is Lost Analysis Quality | Analysis Quality |
| TC-R2-07 | Partially Structured Outline Analysis | Analysis Quality |
| TC-R2-08 | Catalyst Analysis (Regression) | Regression |

## Success Criteria

UAT Round 2 will be considered successful if:

1. Testers confirm the critical UI/UX confusion from Round 1 is resolved
2. Testers confirm the confusion between "All Is Lost" / "Dark Night of the Soul" definitions/analysis is resolved
3. Feedback Quality ratings show noticeable improvement (e.g., average improvement score >= 3.5/5)
4. No new critical bugs related to core functionality are introduced by the fixes

## Timeline

- **Testing Phase**: [Date Range]
- **Debrief Session**: [Date and Time]
- **Results Analysis**: [Date Range]

## Contact Information

- **Test Coordinator**: [Name], [Email], [Phone]
- **Technical Support**: [Name], [Email], [Phone] 