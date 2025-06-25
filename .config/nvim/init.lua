-- bootstrap lazy.nvim, LazyVim and your plugins
require("config.lazy")

vim.cmd("colorscheme lushwal")
require("lushwal").add_reload_hook({
  vim.cmd("LushwalCompile"),
})
