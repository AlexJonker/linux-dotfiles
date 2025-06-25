return {
  {
    "oncomouse/lushwal.nvim",
    cmd = { "LushwalCompile" },
    dependencies = {
      { "rktjmp/lush.nvim" },
      { "rktjmp/shipwright.nvim" },
    },
  },

  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "lushwal",
    },
  },
}
