var fs = require('fs');
var AWS = require('aws-sdk');
var path = require('path');

SECRET_FILE_NAME = '.lamvery_secret.json';
ENV_FILE_NAME = '.lamvery_env.json';
SECRET_DIR = '/tmp/.lamvery-secret';

module.exports = {
    secret: {
        get: function(name, func) {
            fs.readFile(SECRET_FILE_NAME, 'utf-8', function(err, txt) {
                var secret = JSON.parse(txt);
                var kms = new AWS.KMS({region: secret['region']});

                if (!('cipher_texts' in secret)) {
                    func(null, null);
                    return 0;
                }

                if (!(name in secret.cipher_texts)) {
                    func(null, null);
                    return 0;
                }

                kms.decrypt({
                    CiphertextBlob: new Buffer(secret.cipher_texts[name], 'base64')
                }, function(err, data) {
                    func(err, data['Plaintext'].toString('utf-8'))
                });
            });
        },
        file: function(name, func) {
            fs.readFile(SECRET_FILE_NAME, 'utf-8', function(err, txt) {
                var secret = JSON.parse(txt);
                var kms = new AWS.KMS({region: secret['region']});

                if (!('secret_files' in secret)) {
                    func(null, null);
                    return 0;
                }

                if (!(name in secret.secret_files)) {
                    func(null, null);
                    return 0;
                }

                fs.mkdir(SECRET_DIR, function(err) {
                    if (err) {
                        func(err, null)
                    } else {
                        kms.decrypt({
                            CiphertextBlob: new Buffer(secret.secret_files[name], 'base64')
                        }, function(err, data) {
                            if (err) {
                                func(err, null)
                            } else {
                                p = path.join(SECRET_DIR, name);
                                fs.writeFile(p, data['Plaintext'].toString('utf-8') , function(err) {
                                    if (err) {
                                        func(err, null)
                                    } else {
                                        func(err, p)
                                    }
                                });
                            }
                        });
                    }
                });
            });
        }
    },
    env: {
        load: function() {
            try {
                var env = require('./' + ENV_FILE_NAME)
                for (var k in env) {
                    process.env[k] = env[k]
                }
          } catch (err) {}
        }
    }
};
