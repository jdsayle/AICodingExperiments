This is the root folder of my repo of AI-Assisted Coding Experiments. Although so-called "Vibe Coding" will allow someone to quickly push out an MVP or iterate over 
an application with little know how or even understanding of the underlying code, my goals with these experiments are and always will be:
1) *DO ONE THING WELL* - Create a "focused" application to accomplish a well-defined task
2) *KNOW THY CODE* - I don't need to understand every nuance of an apps underlying code and simple is better than complex. That said, it's still important to understand
   what is happening "under the hood" at least at a high-level than to just have some 'magic' running the show
3) *USE THE TOOLS YOU HAVE* - AI Coding assistants can provide great guidance, and do heavy lifting to help speed up development. Ultimately, these experiments are to
   help me gain a better understanding of the capabilities (and limitations) of AI as a coding assistant, not build the next Silicon Valley darling.

   
### My current tooling and workflows
- Google Gemini web interface: broad design exploration, alternative architecture ideas, naming conventions, art generation, second opinions and brainstorming
- VS Code assistant: inspect the real project, edit specific files, trace imports and data flow, run checks, and fix regressions
- GitHub: history, rollback, issue tracking, branches, and eventually backups or collaboration


### AI ASSISTED CODING TIPS
1. **Validate after each meaningful change.**\
   A useful loop is:
    - inspect (or direct the agent to inspect) the relevant files
    - make ONE focused edit, not broad re-writes - e.g. Add validation to the campaign name field. Preserve the current layout and data model. First inspect the relevant Svelte component and its form action, then make the smallest change necessary.
    - run the relevant test, typecheck, or lint command
    - inspect in the browser/dev environment
    - commit changes once you have validated changes
      
2. **Save Frequently, Save Often.**
   Git Commit is your friend. Use Git as the experiment boundary. Before implementing a risky feature, make a commit. These three adages will save you time and headaches.

3. **Be Token Conscious**
   For example: "Inspect only the files relevant to this bug. Do not summarize unrelated code. Make the smallest possible change, then run one focused validation command."
   Will use less tokens than, "Here's a bug, please fix it." Again, AI is the tool here, if you're burning through tokens or have a genuinely big challenge you need to pass to
   the AI, ask it how best to write the prompt so that it uses only the tokens necessary and remains focused on the issue at hand. 

5. **Useful Habits**
- Ask about one feature or error at a time.
- Point to a specific file or route when possible.
- Request concise explanations.
- Have me inspect before editing, then validate the narrow change.
- Avoid pasting entire source files when the workspace is available.
- Use a lower-cost or included model for routine edits and reserve stronger models for architecture or difficult debugging.

~~~~~~~~~~~
TO DO's
  1. Research AGENTS.md or VS Code instruction files to assist the AI Agents and reduce introduction of regressions
