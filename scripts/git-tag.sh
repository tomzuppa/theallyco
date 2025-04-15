#!/bin/bash

echo "📝 Enter your commit message:"
read commit_msg

echo "🏷️ Enter tag name (e.g. v0.3):"
read tag_name

# Confirmación
echo "🚀 About to commit with message: \"$commit_msg\" and tag: $tag_name"
read -p "👉 Continue? (y/n): " confirm

if [ "$confirm" = "y" ]; then
  git add .
  git commit -m "$commit_msg"
  git push origin main
  git tag $tag_name
  git push origin $tag_name
  echo "✅ Done: commit + tag $tag_name pushed!"
else
  echo "❌ Cancelled."
fi
