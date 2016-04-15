import os
import time
import pypandoc
import lamvery

os.system("python setup.py install")

f = open('README.txt', 'w+')
f.write(pypandoc.convert('README.md', 'rst'))
f.close()
os.system("python setup.py sdist upload")
os.remove('README.txt')

time.sleep(120)

os.system("git tag v{}".format(lamvery.__version__))
os.system("git push origin v{}".format(lamvery.__version__))
