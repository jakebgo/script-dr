# Script Doctor - User Acceptance Testing Plan

## 1. Purpose and Scope

This User Acceptance Testing (UAT) plan outlines the approach, resources, and schedule for testing the Script Doctor application from the perspective of end users. The primary goal is to validate that the application meets the requirements of screenwriters and provides valuable, actionable feedback on screenplay beat structure according to the Save the Cat methodology.

### Objectives:
- Validate the application's functionality against user requirements
- Assess the quality and relevance of the screenplay beat analysis
- Evaluate the usability of the interface
- Identify any issues, bugs, or areas for improvement
- Collect user feedback to guide future development

## 2. Test Environment

### Requirements:
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Access to the Script Doctor application instance
- No special hardware requirements
- Test data (screenplay outlines)

### Setup Instructions:
1. Ensure the Script Doctor application is running on the test server
2. Verify API key for Gemini Pro is active and has sufficient quota
3. Confirm ChromaDB is properly initialized with the Save the Cat framework document
4. Prepare test users with login credentials if applicable
5. Distribute test data and instructions to testers

## 3. Test Data

### Sample Screenplay Outlines
Five sample screenplay outlines of varying complexity and quality:

1. **Well-Structured Outline**: A complete outline following Save the Cat principles closely
2. **Partially Structured Outline**: An outline with some beats implemented well, others missing or weak
3. **Problematic Outline**: An outline with intentional structural issues and missing setups
4. **Genre-Specific Outline**: An outline representing a specific genre (e.g., action, romance)
5. **Complex Narrative Outline**: An outline with multiple plotlines and complex character arcs

### Beat Types to Test
Test all major beat types from the Save the Cat framework:
- Opening Image
- Theme Stated
- Setup
- Catalyst
- Debate
- Break into Two
- B Story
- Fun and Games
- Midpoint
- Bad Guys Close In
- All Is Lost
- Dark Night of the Soul
- Break into Three
- Finale
- Final Image

## 4. Test Scenarios

### Scenario 1: Basic Functionality
**Objective**: Verify the core functionality of the application
1. Load the application in the browser
2. Paste the Well-Structured Outline into the text area
3. Highlight a portion of text corresponding to the Catalyst beat
4. Select "Catalyst" from the beat type dropdown
5. Click "Analyze Beat"
6. Verify the analysis is displayed in the Flag->Explain->Suggest format
7. Repeat with different beat types from the same outline

### Scenario 2: Analysis Quality Assessment
**Objective**: Evaluate the quality and relevance of the analysis
1. Paste the Problematic Outline into the text area
2. Highlight a beat with known structural issues
3. Select the appropriate beat type
4. Click "Analyze Beat"
5. Assess if the system correctly identifies the structural issues
6. Evaluate the relevance of the suggestions to fixing the issues
7. Compare with expert analysis of the same beat

### Scenario 3: Edge Cases and Error Handling
**Objective**: Test application behavior with edge cases
1. Test with very short or minimal text highlighted
2. Test with very large outlines
3. Test with beat type that doesn't match the highlighted content
4. Test without internet connection (to simulate API failures)
5. Test with rapid, repeated submissions
6. Verify appropriate error messages and graceful handling

### Scenario 4: User Interface Usability
**Objective**: Evaluate the usability of the interface
1. Assess clarity of instructions and UI elements
2. Test text highlighting functionality across different browsers
3. Evaluate responsiveness of the UI
4. Test on different device types (desktop, tablet, mobile if applicable)
5. Assess accessibility features
6. Evaluate overall user experience flow

## 5. Evaluation Criteria

### Functionality (1-5 scale)
- All features work as expected
- Analysis is generated successfully
- Response times are acceptable
- No critical errors or crashes

### Analysis Quality (1-5 scale)
- **Accuracy**: Correctly identifies structural issues
- **Relevance**: Suggestions align with Save the Cat principles
- **Specificity**: Analysis refers to specific elements in the outline
- **Actionability**: Suggestions are clear and implementable
- **Insight**: Provides value beyond basic structural adherence

### Usability (1-5 scale)
- **Intuitiveness**: Easy to understand and use without training
- **Efficiency**: Tasks can be completed quickly and with minimal effort
- **Satisfaction**: Overall experience is positive and valuable
- **Clarity**: Instructions and feedback are clear and understandable
- **Responsiveness**: Application responds quickly to user actions

### Overall Value (1-5 scale)
- **Utility**: Addresses a real need for screenwriters
- **Time-saving**: Provides analysis faster than manual review
- **Learning**: Helps users understand screenwriting principles
- **Improvement**: Suggestions lead to actual screenplay improvements
- **Recommendation**: Likelihood to recommend to other screenwriters

## 6. Feedback Collection

### Feedback Form Structure
Each tester will complete a feedback form after testing each scenario:

#### Quantitative Feedback
- Rating scales (1-5) for each evaluation criterion
- Yes/No questions for specific functionality checks
- Multiple choice for preference options

#### Qualitative Feedback
- Open-ended questions about the experience
- Specific suggestions for improvement
- Description of any issues encountered
- Most valuable and least valuable aspects

### Sample Questions
1. How easily were you able to highlight and select a beat? (1-5)
2. How accurate was the analysis of the beat's structural function? (1-5)
3. How actionable were the suggestions provided? (1-5)
4. What was the most useful aspect of the analysis?
5. What was the least useful aspect of the analysis?
6. How would you compare this to your usual process of analyzing screenplay structure?
7. What additional features would make this tool more valuable to you?
8. Would you use this tool in your screenwriting process? Why or why not?

## 7. Test Execution

### Test Schedule
- **Preparation Phase**: 2 days (setup, test data preparation)
- **Testing Phase**: 5 days (test execution by users)
- **Analysis Phase**: 3 days (compile and analyze results)

### Tester Roles and Responsibilities
- **Test Coordinator**: Oversees the UAT process, provides support
- **Technical Support**: Assists with technical issues during testing
- **Testers**: Execute test scenarios, provide feedback
- **Analysts**: Compile and analyze test results

### Testing Process
1. Brief testers on the purpose and goals of the application
2. Provide test scenarios and evaluation criteria
3. Allow testers to explore the application independently
4. Have testers execute each test scenario
5. Complete feedback forms after each scenario
6. Conduct a debrief session with all testers
7. Compile results and prioritize findings

## 8. Deliverables

### Test Results
- Summary of test execution (scenarios completed, issues found)
- Consolidated ratings across all evaluation criteria
- Analysis of qualitative feedback
- Prioritized list of issues and suggestions

### Recommendation Report
- Overall assessment of application readiness
- Critical issues that must be addressed
- High-priority improvements for next iteration
- User satisfaction metrics and comparison to goals
- Go/No-Go recommendation for deployment

## 9. Test Cases

### Test Case 1: Catalyst Beat Analysis
**Objective**: Verify accurate analysis of a Catalyst beat
1. Paste the Well-Structured Outline
2. Highlight the section representing the Catalyst
3. Select "Catalyst" from the dropdown
4. Click "Analyze Beat"
5. Expected Result: Analysis correctly identifies the beat's structural function and provides relevant suggestions

### Test Case 2: Midpoint Beat with Issues
**Objective**: Verify system can identify problems in a Midpoint beat
1. Paste the Problematic Outline
2. Highlight the section representing the Midpoint
3. Select "Midpoint" from the dropdown
4. Click "Analyze Beat"
5. Expected Result: Analysis flags the structural issues with the Midpoint and suggests improvements

### Test Case 3: Missing Setup Elements
**Objective**: Verify system can identify missing setups
1. Paste the Partially Structured Outline
2. Highlight a beat that references elements without proper setup
3. Select the appropriate beat type
4. Click "Analyze Beat"
5. Expected Result: Analysis identifies the missing setups and explains their importance

### Test Case 4: Genre-Specific Analysis
**Objective**: Verify analysis considers genre conventions
1. Paste the Genre-Specific Outline
2. Highlight a genre-specific beat
3. Select the appropriate beat type
4. Click "Analyze Beat"
5. Expected Result: Analysis considers genre context in its suggestions

### Test Case 5: UI Responsiveness
**Objective**: Verify UI responsiveness with large outlines
1. Paste the Complex Narrative Outline (large text)
2. Test the text highlighting functionality
3. Select various beat types
4. Click "Analyze Beat" multiple times
5. Expected Result: UI remains responsive and functional with large inputs

## 10. Implementation Plan

### Phase 1: Preparation (Days 1-2)
- Finalize test data preparation
- Set up test environment
- Brief testers on the application and testing process
- Distribute test materials and access instructions

### Phase 2: Execution (Days 3-7)
- Day 3: Test Scenarios 1 and 2
- Day 4: Test Scenarios 3 and 4
- Days 5-6: Complete all test cases
- Day 7: Additional testing based on initial findings

### Phase 3: Analysis and Reporting (Days 8-10)
- Compile all test results and feedback
- Analyze findings and identify patterns
- Prioritize issues and improvement suggestions
- Prepare final UAT report and recommendations

## 11. Success Criteria

The UAT will be considered successful if:
1. All test scenarios are executed by at least 3 testers
2. No critical functionality issues are found
3. Analysis quality achieves an average rating of at least 3.5/5
4. Usability achieves an average rating of at least 4/5
5. At least 70% of testers would recommend the tool to other screenwriters
6. Clear actionable feedback is collected for future improvements

---

## Appendix: Feedback Forms

### Scenario Feedback Form Template

**Tester Name:**  
**Date:**  
**Scenario Tested:**  
**Outline Used:**  
**Beat Type Analyzed:**  

#### Functionality Ratings (1-5)
- Features worked as expected: [ ]
- Analysis was generated successfully: [ ]
- Response times were acceptable: [ ]
- No critical errors or crashes: [ ]

#### Analysis Quality Ratings (1-5)
- Accuracy (correctly identified issues): [ ]
- Relevance (aligned with Save the Cat): [ ]
- Specificity (referenced specific elements): [ ]
- Actionability (suggestions were implementable): [ ]
- Insight (provided valuable perspective): [ ]

#### Usability Ratings (1-5)
- Intuitiveness (easy to understand): [ ]
- Efficiency (tasks completed quickly): [ ]
- Satisfaction (experience was positive): [ ]
- Clarity (instructions were clear): [ ]
- Responsiveness (application responded quickly): [ ]

#### Overall Value Ratings (1-5)
- Utility (addresses real needs): [ ]
- Time-saving (faster than manual review): [ ]
- Learning (helps understand principles): [ ]
- Improvement (leads to better screenplay): [ ]
- Recommendation (would recommend to others): [ ]

#### Open-Ended Feedback
1. What was the most useful aspect of the analysis?
2. What was the least useful aspect of the analysis?
3. What issues or bugs did you encounter?
4. What additional features would improve this tool?
5. How would you compare this to your usual process?
6. Additional comments or suggestions:

---

*This UAT Plan is subject to revision based on project requirements and stakeholder feedback.* 