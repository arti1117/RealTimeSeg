# Utility Scripts

Helper scripts for development and deployment workflows.

## Available Scripts

### Frontend Development
- **start_frontend.sh** - Start frontend server (Linux/Mac)
- **start_frontend.bat** - Start frontend server (Windows)

### Deployment
- **push_to_github.sh** - Automated git commit and push workflow

## Usage

### Linux/Mac
```bash
# Make scripts executable (if needed)
chmod +x scripts/*.sh

# Run script
./scripts/start_frontend.sh
./scripts/push_to_github.sh
```

### Windows
```cmd
scripts\start_frontend.bat
```

## Notes

- Scripts assume you're running from the project root directory
- Frontend scripts start a local HTTP server for development
- Push script includes automated git add, commit, and push workflow
