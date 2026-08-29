local component = require("component")

local args = {...}
local url = args[1]
local path = args[2]

if not url or not path then
  io.stderr:write("usage: download <url> <path>\n")
  return
end

local address = component.list("internet")()
assert(address, "no internet card found")

local internet = component.proxy(address)
local handle, reason = internet.request(url)
assert(handle, reason or "request failed")

local file = assert(io.open(path, "w"))
while true do
  local chunk = handle.read()
  if chunk == nil then
    break
  end
  file:write(chunk)
end
file:close()
handle.close()

print("downloaded " .. path)
