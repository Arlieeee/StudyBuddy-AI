# 1. 创建并没有任何历史记录的临时分支
git checkout --orphan latest_branch

# 2. 添加所有当前文件
git add -A

# 3. 提交更改
git commit -am "Initial commit (History Reset)"

# 4. 删除旧的 main 分支
git branch -D main

# 5. 将当前分支重命名为 main
git branch -m main

# 6. 强制推送到远程仓库
# 注意：这一步会覆盖远程仓库的历史，不可撤销
echo "正在强制推送到远程仓库..."
git push -f origin main
