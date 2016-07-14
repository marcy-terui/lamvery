var lamvery = require('./lamvery.js');
var fs = require('fs');

exports.lambdaHandler = function(event, context) {
    lamvery.env.load();
    console.log(event);
    console.log(process.env);
    lamvery.secret.get('foo', function(err, data) {
        console.log(data);
        lamvery.secret.file('bar.txt', function(err, p) {
            fs.readFile(p, 'utf-8', function(err, txt) {
                console.log(txt);
                context.succeed("done.");
            });
        });
    });
}
