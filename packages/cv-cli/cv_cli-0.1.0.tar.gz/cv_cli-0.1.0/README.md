# Resume Builder
CV CLI is a simple Python script that generates a LaTeX resume using the Jinja2 templating engine. It allows you to create a professional-looking resume in PDF format with minimal effort.

## Features
- Easy to use: Just fill in a YAML file with your information and run the script.
- Multiple Profiles: Supports multiple profiles, allowing you to create different resumes for different job types.
- Customizable: Supports multiple templates and allows you to create your own.
- Output in PDF format: Generates a high-quality PDF resume using LaTeX.
- Cross-platform: Works on Windows, macOS, and Linux.

## Resume Previews
| Default Template | Sheets Template |
|------------------|-----------------|
| ![Default Template](previews/default.png) | ![Sheets Template](previews/sheets.png) |


## Getting Started
### Prerequisites
- Python 3.6 or higher
- LaTeX distribution (e.g., TeX Live, MikTeX) installed on your system

### Installation
Clone the repository:
```bash
   git clone https://github.com/danielaca18/resume-builder.git
   cd resume-builder
   pip install .
```

## Usage
1. Create a YAML file with your resume information. You can use the provided `example.yaml` as a template.
2. Select a template for your resume. You can choose from the provided templates in the `templates` directory or create your own.
3. Run the script to generate your resume:
   ```bash
   cv-cli build -p example -t default
   ```
4. The generated PDF resume will be saved in the `output` directory.

## Acknowledgements
- This project uses the [Resume Template](https://github.com/jakegut/resume) by Jake Gutierrez as a base for the LaTeX templates. Thank you for your work!
- The provided sheets template is inspired by the famous [Sheets Resume](https://sheetsresume.com/resume-template/) by Sheets Resume.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Planned Features
- Git Integration
    - Import & Sync Profiles
    - Import & Sync Templates
- Template Configuration
    - Include files
    - Name templates
- Editor Integration
    - VSCode