local component = require("component")

local args = {...}
local path = args[1] or "storagedrawers_drawer_2x2.holo"
local model = assert(loadfile(path))()

local function applyPalette(h)
  for i, color in ipairs(model.palette) do
    local packed = color[1] * 65536 + color[2] * 256 + color[3]
    h.setPaletteColor(i, packed)
  end
end

local function render(h)
  h.clear()
  h.setScale(1)
  applyPalette(h)

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

  return rendered
end

local count = 0
for address in component.list("hologram") do
  count = count + 1
  local h = component.proxy(address)
  local runs = render(h)
  print("rendered projector " .. tostring(count) .. " " .. address .. " runs=" .. tostring(runs))
end

print("done, projectors=" .. tostring(count))
