var mysql = require('mysql');
var pool = mysql.createPool({
    connectionLimit : 10,
    host            : 'oniddb.cws.oregonstate.edu',
    user            : 'scanlonr-db',
    password        : 'miWossoKK6AUHc5g',
    database        : 'scanlonr-db',
    dateStrings     : 'date'
});

module.exports.pool = pool;
