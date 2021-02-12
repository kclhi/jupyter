git lfs pull
while [ $(git rev-list --count HEAD) -gt 1 ]; do git reset --hard HEAD~1; done # Unwinding through the commits seems to prompt git LFS
git pull
echo "abc" >> a.ipynb
git add .
git commit -m "Unprotect head"
bfg --delete-folders RDownloads .
bfg --delete-folders Rlib .
bfg --delete-folders R_libraries .
bfg --delete-folders anaconda3 .
bfg --strip-blobs-bigger-than 100M .
bfg --delete-files *.tiff .
bfg --delete-files *.zip .
bfg --delete-files *.tar.gz .
bfg --delete-files *.shp .
# TODO: properly remove git lfs, e.g. https://github.com/git-lfs/git-lfs/issues/3026
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git rm a.ipynb
git reset --hard HEAD~1
