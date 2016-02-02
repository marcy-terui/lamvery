var lamvery = require('./lamvery.js');

exports.lambdaHandler = function(event, context) {
    console.log(event);
    lamvery.secret.get('foo', function(err, data) {
        console.log(data);
        context.succeed("done.");
    });
}
