#!/bin/bash

echo "🚀 Pushing fixes to GitHub..."
echo ""
echo "If this fails with authentication error, you have 3 options:"
echo ""
echo "Option 1: Use GitHub CLI"
echo "  gh auth login"
echo "  git push origin main"
echo ""
echo "Option 2: Use Personal Access Token"
echo "  git push https://YOUR_TOKEN@github.com/arti1117/RealTimeSeg.git main"
echo ""
echo "Option 3: Use SSH (if configured)"
echo "  git remote set-url origin git@github.com:arti1117/RealTimeSeg.git"
echo "  git push origin main"
echo ""
echo "Attempting push..."
git push origin main
