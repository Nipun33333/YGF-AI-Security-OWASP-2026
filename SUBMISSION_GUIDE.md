# Submission guide | YGF AI Security Internship | 14 November 2026

## Deliverables prepared

1. GitHub-ready source: `app.py`, `security_lab.py`, `providers.py`, `run_tests.py`, README, Dockerfile, test suite, cases JSON.
2. Report: `docs/YGF_AI_Security_OWASP_2026_Report.pdf` (8 pages).
3. Results sheet: `docs/YGF_OWASP_2026_Results.xlsx`; 132 rows, marked as **fixture only**.
4. Narrated explanatory demo video: `docs/YGF_OWASP_2026_Demo.mp4` (~9 minutes). Includes reconstructed local UI frames based on actual fixture outputs, not an authenticated screen recording of cloud AI models.
5. Results CSV: `results/fixture_results.csv`.

## Why this is not a fully completed submission yet

- Real Claude and Gemini calls were **not** executed because API credentials were not available. The assignment explicitly asks for actual comparative model testing. Fixtures do not satisfy that part, even though they demonstrate the application mitigations.
- A remote GitHub repository **has not been created/published**; code is ready to upload as its own new repository.
- The Google Form **has not been submitted**. Do not mark it as submitted until the live results and links exist.
- The MCP POC is a connection-policy **simulation**, not an interoperable live MCP server-client connection.

## Run app locally

```bash
python app.py
```

Open http://127.0.0.1:8765 on the same computer.

```bash
python run_tests.py --mode fixture --provider both
python -m unittest discover -s tests -v
```

## Run real provider text probes before submission

1. Securely obtain your **own** Claude and Gemini API keys from the providers' official platforms. Never give them to an applicant reviewer, paste them in chat, or commit them to GitHub.
2. Install the dependencies with `python -m pip install -r requirements.txt`.
3. Configure `ANTHROPIC_API_KEY` and `GEMINI_API_KEY` as environment variables using your local shell or OS settings.
4. Run `python run_tests.py --mode live --provider both --output results/live_results.csv`.
5. Review the real responses for false positives and refusals and prepare an updated report/spreadsheet. Do not claim model-tool exploit outcomes from these text-only probes.

## GitHub upload (new repository only)

Create a new GitHub repository, for example `ygf-owasp-ai-security-poc-2026`, and upload the project source/files. Do not upload `.env` or your live unredacted responses. Do not put these files in an unrelated existing repository.

## Google Form submission

Open: https://docs.google.com/forms/d/e/1FAIpQLSeAVR9QBLuQKnH3L5Rgkapb_yQHW4ocoHnTsMweJ6yf1GHVYA/viewform?usp=publish-editor

Enter your personal data truthfully, add the new GitHub repository URL, link to your PDF report/results sheet/demo video hosted where the form permits, and submit **before 14 November 2026**. If the form instead requires file uploads, upload the corresponding files directly. The exact form fields were not accessible to the author at creation time.

**Do not upload or submit the work as completed real-model testing without performing the live tests and updating the report.**