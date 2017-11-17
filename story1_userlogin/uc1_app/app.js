// SETUP
var express = require('express');
var mysql = require('mysql');
var db_connection = mysql.createConnection({
  host  : 'oniddb.cws.oregonstate.edu',
  user  : 'scanlonr-db',
  password : 'miWossoKK6AUHc5g',
  database : 'scanlonr-db'
});
db_connection.connect();
//var mysql = require('./dbcon.js');
var bodyParser = require('body-parser');
var app = express();
var handlebars = require('express-handlebars').create({defaultLayout:'main'});
app.engine('handlebars', handlebars.engine);
app.set('view engine', 'handlebars');
var portArg = 3000;
if (process.argv[2]) {
  portArg = process.argv[2];
}
if (portArg < 1024 || portArg > 65535) {
  portArg = 3000;
}
app.set('port', portArg);
app.use(express.static('public'));
app.use(bodyParser.urlencoded({ extended: false}));
app.use(bodyParser.json());

// HOME PAGE
app.get('/', function(req, res, next) {
  var context = {};
  db_connection.query("SELECT * FROM inmate",
    function(err, rows, fields) {
      console.log("ERROR:");
      console.log(err);
      console.log("ROWS:");
      console.log(rows);
      console.log("FIELDS");
      console.log(fields);
    });
  //mysql.pool.query('select * from inmate',
    //function(err, rows, fields) {
      //if (err) {
        //next(err);
        //return;
      //}
      //context = rows[0];
      //console.log(context);
  //});
  //res.render('test', context);
})

//// test without db
//app.get('/', function(req, res, next) {
  //context = {};
  //context.fname = "test first name";
  //context.minit = "test middle inint";
  //context.lname = "test last name";
  //context.dob = "test DOB";
  //context.wallet = "test balance";
  //context.username = "myusername";
  //context.password = "mypassword";
  //res.render('test', context);
//})

// 404 PAGE
app.use(function(req, res) {
  res.status(404);
  res.render('404');
});

// 500 PAGE
app.use(function(err, req, res, next) {
  console.error(err.stack);
  res.status(500);
  res.render('500');
});

/// LISTEN ON CHOSEN PORT
app.listen(app.get('port'), function(){
  console.log('Express started on http://localhost:' + app.get('port') +
  '; press Ctrl-C to terminate.');
});

