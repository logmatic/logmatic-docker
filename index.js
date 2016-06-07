#! /usr/bin/env node

'use strict';

var net = require('net');
var eos = require('end-of-stream');
var through = require('through2');
var allContainers = require('docker-allcontainers');
var logFactory = require('docker-loghose');
var statsFactory = require('docker-stats');
var eventsFactory = require('docker-event-log');
var minimist = require('minimist');


function parseOptions(){
  var apiKey = process.argv[2];

  if(apiKey==null){
    console.log('You must define your Logmatic.io\'s api key as a first argument.\n' +
      '> logmatic-docker [apiKey] \n' +
                '   [-a ATTR (eg myattribute="my attribute")]\n' +
                '   [-h HOSTNAME (default "api.logmatic.io")] [-p PORT (default "10514")]\n' +
                '   [--matchByImage REGEXP] [--matchByName REGEXP]\n' +
                '   [--skipByImage REGEXP] [--skipByName REGEXP]\n' +
                '   [--no-dockerEvents]\n' +
                '   [--no-logs]\n' +
                '   [--no-stats] [-i statsInterval]\n')

    process.exit(1);
  }

  var opts = minimist(process.argv.slice(3),{
              boolean: ["debug", "stats", "dockerEvents"],
              alias: {
                attr: "a",
                host: "h",
                port: "p",
                statsinterval: 'i'
              },
              default:{
                newline: true,
                stats: true,
                logs: true,
                dockerEvents: true,
                host: 'api.logmatic.io',
                port: '10514',
                apiKey: apiKey,
                statsinterval: 30
              }
            });

  //Parse extra attributes
  if(opts.attr){
    if(!Array.isArray(opts.attr)){
      opts.attr = [opts.attr];
    }
    var extra_attributes = {};
    for (var i in opts.attr) {
      var keyvalue = opts.attr[i].split('=');
      extra_attributes[keyvalue[0]] = keyvalue[1];
    }
    opts.attr = extra_attributes;
  }

  if(opts.debug){
    console.log("> Options:\n",opts);
  }
  return opts;
}

function merge(object, into) {
    if (!object) { return; }

    var key;
    for (key in object) {
      if (object.hasOwnProperty(key)) {
        into[key] = object[key];
    }
  }
}

function start() {
  var opts = parseOptions();

  var filter = through.obj(function(obj, enc, cb) {
    merge(opts.attr,obj);

    if (obj.line) {
      obj.message = obj.line;
      delete obj.line;
    }
    else if (obj.type) {
      obj.message = "[Docker event] host=\""+obj.host+"\" name=\""+obj.name+"\" event=\""+obj.type+"\"";
    }

    if(opts.debug){
      console.log("> Send entry:\n",obj);
    }

    this.push(opts.apiKey);
    this.push(' ');
    this.push(JSON.stringify(obj));
    this.push('\n');

    cb()
  });

  var events = allContainers(opts);
  var streamsOpened = 0;

  if (opts.logs) {
      var loghose = logFactory(opts);
      loghose.pipe(filter);
      streamsOpened++;
  }

  if (opts.stats) {
      var stats = statsFactory(opts);
      stats.pipe(filter);
      streamsOpened++;
  }


  if (opts.dockerEvents) {
      var dockerEvents = eventsFactory(opts);
      dockerEvents.pipe(filter);
      streamsOpened++;
  }

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

    out = net.createConnection(opts.port, opts.host);
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
