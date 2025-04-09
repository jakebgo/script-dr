# Script Doctor - UAT Round 2 Test Execution Guide

## Introduction

This guide provides step-by-step instructions for executing the test cases for UAT Round 2. The focus of this round is to validate that the critical issues identified in Round 1 have been successfully addressed:

1. UI/UX issues with the dual text area design
2. Beat definition confusion (especially between "All Is Lost" and "Dark Night of the Soul")
3. Analysis quality and relevance

## Before You Begin

1. **Access**: Navigate to http://localhost:8000 to access the Script Doctor application
2. **Test Data**: Use the provided outline files from the `data/uat_samples/` directory:
   - `well_structured_outline.txt`
   - `partially_structured_outline.txt`
   - `problematic_outline.txt`
3. **Feedback**: Use the provided feedback form to document your observations for each test case
4. **Browser**: Use the same browser you used for Round 1 testing if possible

## Test Cases

### Scenario 1: UI/UX Validation

#### TC-R2-01: Basic UI Workflow

**Objective**: Verify the redesigned UI (single text area) is intuitive and solves previous confusion.

**Prerequisites**: 
- Access to the Script Doctor application
- Copy of `well_structured_outline.txt`

**Steps**:
1. Open the application in your browser
2. Copy the content of `well_structured_outline.txt`
3. Paste it into the single text area
4. Find and highlight the section labeled "CATALYST" (including heading and paragraph)
5. Select "Catalyst" from the beat type dropdown
6. Click "Analyze Beat"
7. Wait for the analysis to complete

**Expected Results**:
- The text should be properly pasted into the text area
- The highlight selection should work smoothly
- The beat type selection should be clear
- After clicking "Analyze Beat", results should appear in the Flag->Explain->Suggest format

**Evaluation Criteria**:
- Rate the ease of use compared to the previous dual text area design
- Assess the clarity of the highlighting workflow
- Note any usability issues or confusion points

#### TC-R2-02: Visual Feedback Validation

**Objective**: Verify the visual feedback elements work as expected to guide the user.

**Prerequisites**: 
- Access to the Script Doctor application
- Copy of any sample outline

**Steps**:
1. Open the application in your browser
2. Copy and paste any outline into the text area
3. Highlight a section of text
4. Observe if the "Selected Text" confirmation appears below the text area
5. Select a beat type from the dropdown
6. Click "Analyze Beat" 
7. Observe the loading indicator during analysis

**Expected Results**:
- A confirmation of your text selection should appear
- When analyzing, a loading spinner or indicator should display
- The beat reference section should show the appropriate description for the selected beat type

**Evaluation Criteria**:
- Rate the effectiveness of the visual feedback indicators
- Assess whether the application provides clear guidance during the workflow
- Note any missing or confusing feedback elements

### Scenario 2: Beat Definition Accuracy Validation

#### TC-R2-03: All Is Lost Beat Definition

**Objective**: Confirm the fix for the "All Is Lost" beat definition retrieval.

**Prerequisites**: 
- Access to the Script Doctor application
- Copy of `problematic_outline.txt`

**Steps**:
1. Open the application in your browser
2. Copy and paste the content of `problematic_outline.txt`
3. Find and highlight the paragraph labeled "ALL IS LOST"
4. Select "All Is Lost" from the beat type dropdown
5. Click "Analyze Beat"
6. Review the analysis results, particularly the "Explain" section

**Expected Results**:
- The "Explain" section should specifically reference All Is Lost principles
- The explanation should focus on the "lowest moment" or "major setback" aspects
- The content should not be confused with Dark Night of the Soul principles

**Evaluation Criteria**:
- Verify the explanation correctly references All Is Lost principles
- Check that there's no confusion with Dark Night of the Soul concepts
- Note the specificity and accuracy of the beat definition referenced

#### TC-R2-04: Dark Night of the Soul Beat Definition

**Objective**: Confirm the fix for the "Dark Night of the Soul" beat definition retrieval.

**Prerequisites**: 
- Access to the Script Doctor application
- Copy of `problematic_outline.txt`

**Steps**:
1. Open the application in your browser
2. Copy and paste the content of `problematic_outline.txt`
3. Find and highlight the paragraph labeled "DARK NIGHT OF THE SOUL"
4. Select "Dark Night of the Soul" from the beat type dropdown
5. Click "Analyze Beat"
6. Review the analysis results, particularly the "Explain" section

**Expected Results**:
- The "Explain" section should specifically reference Dark Night of the Soul principles
- The explanation should focus on reflection, despair, or inner turmoil aspects
- The content should be distinct from the All Is Lost explanation (TC-R2-03)

**Evaluation Criteria**:
- Verify the explanation correctly references Dark Night of the Soul principles
- Confirm it's clearly distinct from the All Is Lost explanation seen in TC-R2-03
- Note the specificity and accuracy of the beat definition referenced

#### TC-R2-05: Well-Defined Beat (Midpoint)

**Objective**: Verify correct beat definition retrieval for a well-defined beat.

**Prerequisites**: 
- Access to the Script Doctor application
- Copy of `well_structured_outline.txt`

**Steps**:
1. Open the application in your browser
2. Copy and paste the content of `well_structured_outline.txt`
3. Find and highlight the paragraph labeled "MIDPOINT"
4. Select "Midpoint" from the beat type dropdown
5. Click "Analyze Beat"
6. Review the analysis results, particularly the "Explain" section

**Expected Results**:
- The "Explain" section should specifically reference Midpoint principles
- The explanation should mention concepts like "raising the stakes" or "false victory/defeat"

**Evaluation Criteria**:
- Verify the explanation correctly references Midpoint principles
- Assess the accuracy and relevance of the beat definition
- Note any generic versus specific content in the explanation

### Scenario 3: Analysis Quality & Relevance Validation

#### TC-R2-06: All Is Lost Analysis Quality

**Objective**: Assess the quality and actionability of the analysis for a problematic beat.

**Prerequisites**: 
- Access to the Script Doctor application
- Completed TC-R2-03 (All Is Lost Beat Definition)

**Steps**:
1. Review the complete analysis results from TC-R2-03
2. Focus on all three sections: Flag, Explain, and Suggest
3. If you participated in Round 1, mentally compare to previous results

**Expected Results**:
- The "Flag" section should clearly identify a specific issue with the beat
- The "Explain" section should provide context using Save the Cat principles
- The "Suggest" section should offer specific, actionable recommendations

**Evaluation Criteria**:
- Rate the clarity of the flagged issue (is it specific and relevant?)
- Assess the accuracy of the explanation (does it reference relevant principles?)
- Evaluate the actionability of suggestions (are they specific to the outline?)
- Rate the overall improvement compared to Round 1 (if applicable)

#### TC-R2-07: Partially Structured Outline Analysis

**Objective**: Assess how well the system analyzes a beat with structural issues.

**Prerequisites**: 
- Access to the Script Doctor application
- Copy of `partially_structured_outline.txt`

**Steps**:
1. Open the application in your browser
2. Copy and paste the content of `partially_structured_outline.txt`
3. Find and highlight the paragraph labeled "MIDPOINT"
4. Select "Midpoint" from the beat type dropdown
5. Click "Analyze Beat"
6. Review the complete analysis, focusing on setup issues identified

**Expected Results**:
- The analysis should identify structural issues with the Midpoint
- The "Explain" section should reference relevant Save the Cat principles
- The "Suggest" section should offer specific advice for improving the Midpoint

**Evaluation Criteria**:
- Assess how well the analysis identifies setup issues
- Evaluate the relevance of the suggestions to the specific issues identified
- Rate the clarity and actionability of the feedback
- Note how well the setup check is integrated into the overall analysis

### Scenario 4: Basic Regression Check

#### TC-R2-08: Catalyst Analysis (Regression)

**Objective**: Ensure remediation fixes haven't negatively impacted analysis of well-structured beats.

**Prerequisites**: 
- Access to the Script Doctor application
- Copy of `well_structured_outline.txt`

**Steps**:
1. Open the application in your browser
2. Copy and paste the content of `well_structured_outline.txt`
3. Find and highlight the paragraph labeled "CATALYST"
4. Select "Catalyst" from the beat type dropdown
5. Click "Analyze Beat"
6. Review the complete analysis for quality and accuracy

**Expected Results**:
- The application should produce a reasonable, structurally sound analysis
- The response should acknowledge the strengths of a well-implemented Catalyst
- The system should complete the analysis without errors

**Evaluation Criteria**:
- Verify the analysis is relevant to the Catalyst beat
- Assess whether the system recognizes a well-structured beat
- Note any regression issues compared to previous functionality
- Check for any unexpected behaviors or errors

## Reporting Issues

If you encounter any issues during testing:
1. Document the issue in the feedback form
2. Note the exact steps to reproduce the issue
3. Take a screenshot if applicable
4. Include any error messages that appeared
5. Continue with the remaining test cases if possible

## Submitting Feedback

After completing each test case:
1. Fill out a separate feedback form for each test case
2. Be as specific as possible in your comments
3. Save the form with the naming convention: `[Your Name]_[Test Case ID]_feedback.md`
4. Submit your feedback to the test coordinator

Thank you for your participation in UAT Round 2! 