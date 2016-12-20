import os
import time
import pypandoc
import lamvery

os.system("python setup.py install")

os.system("pandoc README.md --from=markdown --to=rst > README.txt")
os.system("python setup.py sdist upload")
os.remove('README.txt')

time.sleep(120)

os.system("git tag v{}".format(lamvery.__version__))
os.system("git push origin v{}".format(lamvery.__version__))
