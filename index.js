#! /usr/bin/env node

'use strict';

var net = require('net');
var eos = require('end-of-stream');
var through = require('through2');
var allContainers = require('docker-allcontainers');
var logFactory = require('docker-loghose');
var eventsFactory = require('docker-event-log');

function start() {
  var apiKey = process.argv[2];
  if(apiKey==null){
    console.log('You must define your Logmatic.io\'s api key as a first argument.');
    process.exit(1);
  }

  var opts = {
      server: 'api.logmatic.io',
      port: '10514',
      apiKey: apiKey,
  };

  var filter = through.obj(function(obj, enc, cb) {

    if (obj.line) {
      obj.message = obj.line;
      delete obj[line];
    }
    else if (obj.type) {
      obj.message = "[Docker event] host=\""+obj.host+"\" name=\""+obj.name+"\" event=\""+obj.type+"\"";
    }

    this.push(apiKey);
    this.push(' ');
    this.push(JSON.stringify(obj));
    this.push('\n');

    cb()
  });

  var events = allContainers(opts);
  var streamsOpened = 0;

  var loghose = logFactory(opts);
  loghose.pipe(filter);
  streamsOpened++;

  var dockerEvents = eventsFactory(opts);
  dockerEvents.pipe(filter);
  streamsOpened++;

  pipe();

  // destroy out if all streams are destroyed
  loghose && eos(loghose, function() {
    streamsOpened--;
    streamClosed(streamsOpened);
  });
  dockerEvents && eos(dockerEvents, function() {
    streamsOpened--;
    streamClosed(streamsOpened);
  });

  return loghose;

  var out;
  var noRestart = function() {};

  function pipe() {
    if (out) {
      filter.unpipe(out);
    }

    out = net.createConnection(opts.port, opts.server);
    filter.pipe(out, { end: false });
    noRestart = eos(out, pipe);
  }

  function streamClosed(streamsOpened) {
    if (streamsOpened <= 0) {
      noRestart()
      out.destroy();
    }
  }
}

module.exports = start;

if (require.main === module) {
  start();
}
