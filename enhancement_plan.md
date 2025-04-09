# Script Doctor - Enhancement Plan

Based on the successful completion of UAT Round 2, this document outlines the planned enhancements to address the minor issues identified during testing. These enhancements will focus on improving the specificity and contextual awareness of the analysis without requiring significant architectural changes.

## Enhancement Goals

1. **Improve Cross-Beat References**: Enhance the system's ability to reference related beats when explaining setup issues
2. **Increase Location Specificity**: Provide more precise guidance on where in the outline to make suggested changes
3. **Prepare for Limited Release**: Address any final details needed for broader user testing

## 1. Cross-Beat Analysis Enhancement

### Problem Statement
Currently, when analyzing a beat's setup issues, the system identifies problems but doesn't always reference which specific previous beats should be modified to address those issues. For example, when analyzing the All Is Lost beat, it might not reference how the Bad Guys Close In beat failed to set up the necessary context.

### Proposed Solution
1. **Enhanced Beat Indexing**:
   - Extend the outline indexing process to tag and categorize each beat section
   - Create a beat relationship map based on the Save the Cat framework
   - Store beat sequence information as metadata in ChromaDB

2. **Cross-Reference Prompt Enhancement**:
   - Update the analysis pipeline to include a "beat relationship" step
   - Modify prompts to specifically look for connections between the current beat and earlier beats
   - Example prompt addition:
     ```
     When identifying setup issues with this [BEAT_TYPE], explicitly reference which earlier beats (e.g., Setup, Catalyst, B-Story, etc.) should be modified to address these issues. For each suggestion, specify which exact beat should contain the setup elements.
     ```

3. **Implementation Plan**:
   - Update `analyzer.py` to include beat relationship analysis
   - Modify the ChromaDB schema to store beat relationship metadata
   - Enhance prompt templates with cross-reference instructions
   - Add a testing phase specifically for cross-beat references

### Success Criteria
- Analysis results consistently reference specific earlier beats when identifying setup issues
- Suggestions include which exact beats need modification, not just general act references

## 2. Location Specificity Enhancement

### Problem Statement
When suggesting additions or changes, the system sometimes uses general act references (e.g., "Insert scenes through Act Two-A") rather than pointing to specific locations or beat names in the outline.

### Proposed Solution
1. **Beat Name Standardization**:
   - Create a standardized mapping of screenplay sections, acts, and beats
   - Implement a beat position detection algorithm
   - Associate specific line numbers or paragraph indices with beat names

2. **Targeted Suggestion Prompt**:
   - Update the suggestion generation prompt to require location specificity
   - Example prompt addition:
     ```
     For each suggestion, provide a specific location in the outline where the change should be made. Reference the exact beat name (e.g., "Fun & Games," "Debate," etc.) rather than general act references. If suggesting a new scene, specify where it should be placed relative to existing beats.
     ```

3. **Implementation Plan**:
   - Update `document_loader.py` to better recognize and map beat sections
   - Enhance the suggestion generation phase in `analyzer.py`
   - Create a reference guide of standardized beat names and positions
   - Add validation to ensure suggestions include specific locations

### Success Criteria
- Suggestions consistently reference specific beat names rather than general act references
- Users can easily identify exactly where in their outline to make each suggested change

## 3. Limited Release Preparation

### Tasks
1. **Documentation Updates**:
   - Create user guide with simplified instructions
   - Document known limitations and planned improvements
   - Prepare feedback collection mechanisms

2. **Deployment Optimization**:
   - Optimize ChromaDB query performance
   - Implement basic caching for repeated analyses
   - Review and enhance error handling for edge cases

3. **Feedback Mechanism**:
   - Add a simple feedback form in the UI
   - Create a structured database for feedback collection
   - Implement basic analytics to track usage patterns

## Implementation Timeline

| Phase | Description | Timeline | Dependencies |
|-------|-------------|----------|--------------|
| 1 | Cross-Beat Analysis Enhancement | 1 week | None |
| 2 | Location Specificity Enhancement | 1 week | Phase 1 |
| 3 | Limited Release Preparation | 1 week | Phases 1-2 |
| 4 | Testing and Validation | 3 days | Phases 1-3 |
| 5 | Limited Release | 1 day | Phase 4 |

## Required Resources

- Development: 1 engineer, 3 weeks
- Testing: 1 tester, 1 week
- Documentation: 1 technical writer, 1 week

## Success Metrics

- 90% of analysis results include specific beat references when identifying setup issues
- 100% of suggestions include specific beat names or locations for changes
- Positive feedback from limited release users on the specificity and actionability of suggestions

## Conclusion

These enhancements will address the minor issues identified during UAT Round 2 while maintaining the significant improvements already achieved. By focusing on cross-beat references and location specificity, the Script Doctor application will provide even more valuable, actionable feedback to screenwriters. 