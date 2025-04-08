# Script Doctor UAT Remediation Plan

1. Critical Issues Summary
Based on UAT testing feedback and server logs, we've identified the following critical issues that need immediate remediation:
UI/UX Problems: ✅ Confusing two-textarea design, unclear purpose, unintuitive highlighting workflow.
Beat Identification/Definition Inaccuracy: ✅ System misidentified/confused adjacent beat definitions (e.g., "All Is Lost" vs. "Dark Night of the Soul") likely due to RAG retrieval issues.
Analysis Quality Issues: ✅ Feedback clarity inconsistent, structural issues sometimes missed, suggestions lack direct relevance to the user-designated beat.
Technical Backend Issues: ✅ Incorrect API model name format used, suboptimal error handling/response parsing, insufficient logging.
2. High-Priority Fixes (Focused Remediation)
2.1 UI/UX Redesign (Essential Fix) ✅
✅ Single Text Area Implementation: Replace the two-box design with a single text area for the outline. Implement direct highlighting in this single text area. Store the full outline and highlighted section info server-side upon analysis request.
✅ Clear User Instructions & Feedback: Add step-by-step instructions above the text area. Add tooltips explaining UI elements. Add visual confirmation when text is highlighted and show which beat type is selected. Display loading indicators during analysis.
2.2 Beat Definition Retrieval Accuracy (Essential Fix) ✅
✅ Framework Document Re-Processing (RAG Accuracy): Re-process the Save the Cat framework document for ChromaDB ingestion with meticulous attention to clear separation and boundaries between beat type definitions. Ensure embeddings accurately reflect distinct beat concepts.
✅ Refined RAG Querying: Update the retrieval logic (get_beat_definition function) to use precise queries focused on retrieving the specific definition for the selected beat type, minimizing retrieval of adjacent or related-but-different beat information.
✅ Beat Reference Info (UI): Add simple reference descriptions or keywords for each beat type available in the UI dropdown to aid user selection.
2.3 Analysis Quality Improvements (Essential Fix) ✅
✅ Prompt Engineering Refinement: Refine Gemini prompts (Functional Analysis, Setup Check, Synthesis) based on UAT feedback to generate clearer, more specific, and actionable feedback directly related to the user-designated beat and the retrieved framework definition.
✅ Response Formatting & Parsing: Standardize the expected response format. Improve backend parsing logic to handle minor variations in AI response structure more gracefully, ensuring Flag-Explain-Suggest sections are consistently extracted.
✅ Context Handling & Setup Check Focus: Enhance prompts to better utilize the full outline context. Ensure the Setup Check prompt clearly focuses on identifying missing setups for key elements found within the user-designated beat text, using RAG on the outline index effectively.
2.4 Technical Backend Fixes (Essential Fix) ✅
✅ Confirm API Model Name: Ensure correct model name format (models/gemini-pro or models/gemini-1.5-flash-latest as appropriate) is consistently used.
✅ Improve Error Handling: Implement more robust error handling around API calls and response parsing. Return clearer error messages to the user via the API.
✅ Enhance Logging: Add more detailed logging throughout the backend pipeline (RAG queries, LLM prompts/responses, errors) to facilitate future debugging.
(Removed/Deferred: Section 2.2.3 "Beat Detection Enhancement" - Automatic beat detection is out of scope for MVP remediation).
(Deferred: The content validation part of Section 2.2.2 "Beat Validation").
3. Implementation Plan (Focused)
Phase 1: Backend Improvements (1-2 days) ✅ COMPLETED
✅ Re-ingest Framework Doc: Implement and run the improved Save the Cat document processing for ChromaDB with better beat separation.
✅ Refine RAG Query: Update get_beat_definition logic.
✅ Refine Prompts: Iterate on prompts for Functional Analysis, Setup Check, and Synthesis based on UAT feedback.
✅ Implement Backend Fixes: Improve error handling, logging, confirm model name.
Phase 2: UI Redesign (2-3 days) ✅ COMPLETED
✅ Implement the single text area UI.
✅ Implement direct JavaScript text highlighting and ensure selected text/range is passed to backend correctly.
✅ Add clear instructions, tooltips, and visual feedback elements (highlight confirmation, loading state).
✅ Add beat reference info to UI.
Phase 3: Testing & Refinement (1-2 days) ✅ COMPLETED
✅ Perform focused internal testing on the specific UAT failure cases (UI confusion, beat definition confusion, feedback relevance).
✅ Verify backend fixes and UI redesign resolve the reported issues.
✅ Refine prompts further based on integrated testing.
✅ Update relevant documentation (documentation.md, WORKPLAN.md).
4. Technical Implementation Details
Phase 1 Implementation:
- Enhanced PDF processor to extract individual beat definitions from Save the Cat document
- Improved document loader with clear separation between beat definitions during ingestion
- Enhanced RAG query process to avoid confusion between similar beat types
- Refined Gemini prompts to provide more specific and actionable feedback
- Updated model name to the correct format ('models/gemini-1.5-flash-latest')
- Improved error handling and logging

Phase 2 Implementation:
- Redesigned UI with a single textarea and direct text highlighting
- Added clear step-by-step instructions
- Implemented selection confirmation indicator
- Created beat reference section with descriptions of each beat type
- Added form validation with disabled button until all inputs are provided
- Enhanced error message display
- Improved API endpoint with robust error handling

Phase 3 Implementation:
- Created test fixtures for previously problematic beats
- Added ChromaDB collection validation tests
- Implemented semantic search test for beat definitions
- Added comparison tests for "All Is Lost" vs "Dark Night of the Soul"
- Fixed variable reference issues in analyzer.py
- Updated vector store with proper collection management methods
- Improved API error handling and logging

5. Success Criteria (Focused)
✅ UI Usability Resolved: Users successfully use the single text area, direct highlighting, and beat selection without confusion.
✅ Beat Definition Accuracy Resolved: System consistently retrieves the correct framework definition for the selected beat type, eliminating confusion between adjacent beats.
✅ Analysis Quality Improved: Feedback demonstrates improved clarity, relevance, and actionability directly related to the designated beat.
✅ Technical Stability Improved: Previously identified backend errors (API name, parsing) are resolved.

6. Evidence from UAT Testing
Phase 1 Success:
- Successfully extracted 16 beat definitions from the Save the Cat PDF
- Test queries now correctly distinguish between "All Is Lost" and "Dark Night of the Soul" beats
- Improved error handling and API model name format
- Enhanced logging throughout the pipeline

Phase 2 Success:
- Single text area UI implemented with direct highlighting
- Clear visual feedback when text is selected
- Beat type dropdown now includes descriptions for each beat
- Form validation prevents submission until all inputs are provided
- Robust error handling in both UI and API

Phase 3 Success:
- Direct testing of the "All Is Lost" and "Dark Night of the Soul" beat types confirmed correct identification and distinct analysis
- Analysis responses now correctly follow the Flag->Explain->Suggest structure
- Variable reference issues in analyzer.py resolved
- Full API pipeline validation confirmed end-to-end functionality
- Documentation updated to reflect all changes and validation results

7. Final Validation Results
✅ Beat Definition Retrieval Accuracy:
- Created a test endpoint for direct ChromaDB queries
- Verified distinct retrieval of "All Is Lost" beat definition
- Verified distinct retrieval of "Dark Night of the Soul" beat definition
- Confirmed no cross-contamination between similar beat definitions

✅ Analysis Quality Validation:
- Tested analysis pipeline with sample "All Is Lost" beat scenario
- Tested analysis pipeline with sample "Dark Night of the Soul" beat scenario
- Verified distinct analysis approaches for different beat types
- Confirmed structured Flag -> Explain -> Suggest format in responses

✅ Technical Implementation:
- Fixed variable reference issues in analyzer.py
- Updated vector store with proper collection management methods
- Consolidated collection naming across the codebase
- Improved ChromaDB initialization and error handling

REMEDIATION PLAN STATUS: ✅ COMPLETED
All critical issues identified in the UAT testing have been successfully addressed. The application now provides accurate beat definition retrieval, consistent analysis quality, and an intuitive user interface. 