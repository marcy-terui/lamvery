import os
import pypandoc
import lamvery

os.system("python setup.py install")

os.system("git tag v{}".format(lamvery.__version__))
os.system("git push origin v{}".format(lamvery.__version__))

f = open('README.txt', 'w+')
f.write(pypandoc.convert('README.md', 'rst'))
f.close()
os.system("python setup.py sdist upload")
os.remove('README.txt')
