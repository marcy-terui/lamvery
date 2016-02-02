var fs = require('fs');
var AWS = require('aws-sdk');

SECRET_FILE_NAME = '.lamvery_secret.json';

module.exports = {
    secret: {
        get: function(name, func) {
            fs.readFile(SECRET_FILE_NAME, 'utf-8', function(err, txt) {
                var secret = JSON.parse(txt)
                var kms = new AWS.KMS({region: secret['region']});

                if (!('cipher_texts' in secret)) {
                    func(err, null);
                    return
                }

                if (!(name in secret.cipher_texts)) {
                    func(err, null);
                    return
                }

                kms.decrypt({
                    CiphertextBlob: new Buffer(secret.cipher_texts[name], 'base64')
                }, function(err, data) {
                    func(err, data['Plaintext'].toString('utf-8'))
                });
            });
        }
    }
};
