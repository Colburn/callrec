inputFile='/path/to/file'
targetFile'/path/to/target'

fixedUsers=[]
capsUsers=[]

with open(inputFile, 'r') as ogFile:
  users=ogFile.readlines()

for user in users:
   fixedUsers.append(user.replace('\n', ''))

for user in fixedUsers:
  if (any(letter.isupper() for letter in user)):
    capsUsers.append(user)

with open(targetFile, 'a+') as newFile:
  for user in capsUsers:
    newFile.write(user + '\n')
