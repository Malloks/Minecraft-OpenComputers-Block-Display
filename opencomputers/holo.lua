local component = require("component")

local args = {...}
local path = args[1] or "storagedrawers_drawer_2x2.holo"
local address = component.list("hologram")()
assert(address, "no hologram projector found")

local h = component.proxy(address)
local model = assert(loadfile(path))()

h.clear()
h.setScale(1)

for i, color in ipairs(model.palette) do
  local packed = color[1] * 65536 + color[2] * 256 + color[3]
  h.setPaletteColor(i, packed)
end

local rendered = 0

if model.data then
  for run in string.gmatch(model.data, "[^;]+") do
    local values = {}
    for n in string.gmatch(run, "[^,]+") do
      values[#values + 1] = tonumber(n)
    end
    local x, y, z, length, value = values[1], values[2], values[3], values[4], values[5]
    for dx = 0, length - 1 do
      h.set(x + dx, y, z, value)
    end
    rendered = rendered + 1
  end
else
  for _, run in ipairs(model.runs) do
    local x, y, z, length, value = run[1], run[2], run[3], run[4], run[5]
    for dx = 0, length - 1 do
      h.set(x + dx, y, z, value)
    end
    rendered = rendered + 1
  end
end

print("rendered " .. tostring(rendered) .. " hologram runs")
