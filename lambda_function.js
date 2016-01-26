exports.lambdaHandler = function(event, context) {
   console.log(event);
   console.log(context);
   context.succeed("done.");
}
