#!/usr/bin/env ruby

require 'eventmachine'
require 'rack'
require 'rack/static'

app = Proc.new do |env|
  ['200', {'Content-Type' => 'text/html'}, ['???']]
end
static = Rack::Static.new(app, urls: ["/"], root: 'public', index: 'index.html')
Rack::Handler::WEBrick.run static
