# Utility Scripts

Helper scripts for development and deployment workflows.

## Available Scripts

### Frontend Development
- **start_frontend.sh** - Start frontend server (Linux/Mac)
- **start_frontend.bat** - Start frontend server (Windows)
- **stop_frontend.sh** - Stop frontend server (Linux/Mac)
- **stop_frontend.bat** - Stop frontend server (Windows)

### Deployment
- **push_to_github.sh** - Automated git commit and push workflow

## Usage

### Linux/Mac
```bash
# Make scripts executable (if needed)
chmod +x scripts/*.sh

# Start frontend server
./scripts/start_frontend.sh

# Stop frontend server (when done)
./scripts/stop_frontend.sh

# Push to GitHub
./scripts/push_to_github.sh
```

### Windows
```cmd
# Start frontend server
scripts\start_frontend.bat

# Stop frontend server (when done)
scripts\stop_frontend.bat
```

## Notes

- Scripts assume you're running from the project root directory
- Frontend scripts start a local HTTP server on port 8080
- Push script includes automated git add, commit, and push workflow

## Troubleshooting

### "Address already in use" Error

If you see `OSError: [Errno 98] Address already in use`, it means port 8080 is already being used:

**Solution**: Use the stop script to free the port:
```bash
# Linux/Mac
./scripts/stop_frontend.sh

# Windows
scripts\stop_frontend.bat
```

Then try starting the frontend server again.
