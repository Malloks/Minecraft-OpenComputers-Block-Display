local component = require("component")

local args = {...}
local basePath = args[1] or ""
if basePath ~= "" and string.sub(basePath, -1) ~= "/" then
  basePath = basePath .. "/"
end

local currentFacing = 180
local facings = {
  0, 0, 0,
  90, 90, 90, 90, 90
}
local modelFiles = {
  "01_dust.holo",
  "02_storage_drawer_4slot.holo",
  "03_creative_cobble_gen.holo",
  "04_smeltery_controller.holo",
  "05_atomic_reconstructor.holo",
  "06_ember_copper_cell.holo",
  "07_woot_factory_layout.holo",
  "08_nether_star_crux.holo"
}
local centerX = 24.5
local centerZ = 24.5

local function applyPalette(h, model)
  for i, color in ipairs(model.palette) do
    local packed = color[1] * 65536 + color[2] * 256 + color[3]
    h.setPaletteColor(i, packed)
  end
end

local function rotatePoint(x, z, degrees)
  if degrees == 0 then
    return x, z
  end

  local radians = math.rad(degrees)
  local sin = math.sin(radians)
  local cos = math.cos(radians)
  local dx = x - centerX
  local dz = z - centerZ
  local rx = centerX + dx * cos - dz * sin
  local rz = centerZ + dx * sin + dz * cos

  return math.floor(rx + 0.5), math.floor(rz + 0.5)
end

local function setVoxel(h, x, y, z, value, rotation)
  local rx, rz = rotatePoint(x, z, rotation)
  h.set(rx, y, rz, value)
end

local function targetFacing(index)
  return facings[index] or currentFacing
end

local function render(h, index, model)
  h.clear()
  h.setScale(1)
  applyPalette(h, model)

  local rendered = 0
  local rotation = targetFacing(index) - currentFacing

  if model.data then
    for run in string.gmatch(model.data, "[^;]+") do
      local values = {}
      for n in string.gmatch(run, "[^,]+") do
        values[#values + 1] = tonumber(n)
      end
      local x, y, z, length, value = values[1], values[2], values[3], values[4], values[5]
      for dx = 0, length - 1 do
        setVoxel(h, x + dx, y, z, value, rotation)
      end
      rendered = rendered + 1
    end
  else
    for _, run in ipairs(model.runs) do
      local x, y, z, length, value = run[1], run[2], run[3], run[4], run[5]
      for dx = 0, length - 1 do
        setVoxel(h, x + dx, y, z, value, rotation)
      end
      rendered = rendered + 1
    end
  end

  return rendered, targetFacing(index)
end

local count = 0
for address in component.list("hologram") do
  count = count + 1
  local h = component.proxy(address)
  local modelFile = modelFiles[count]
  if modelFile then
    local path = basePath .. modelFile
    local loader, reason = loadfile(path)
    if loader then
      local model = loader()
      local runs, facing = render(h, count, model)
      print("rendered projector " .. tostring(count) .. " " .. address .. " file=" .. modelFile .. " facing=" .. tostring(facing) .. " runs=" .. tostring(runs))
    else
      print("skipped projector " .. tostring(count) .. " " .. address .. " missing=" .. path .. " reason=" .. tostring(reason))
    end
  else
    print("skipped projector " .. tostring(count) .. " " .. address .. " no model configured")
  end
end

print("done, projectors=" .. tostring(count))
