var lamvery = require('./lamvery.js');

exports.lambdaHandler = function(event, context) {
    lamvery.env.load();
    console.log(event);
    console.log(process.env);
    lamvery.secret.get('foo', function(err, data) {
        console.log(data);
        context.succeed("done.");
    });
}
