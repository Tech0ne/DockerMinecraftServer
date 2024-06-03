filetype plugin indent on
set tabstop=4
set shiftwidth=4
set expandtab
set whichwrap+=<,>,h,l,[,]
set nu rnu
set mouse=
colorscheme vim

call plug#begin()

Plug 'https://github.com/vim-airline/vim-airline'
Plug 'https://github.com/preservim/nerdtree'
Plug 'https://github.com/tpope/vim-commentary'
Plug 'https://github.com/ap/vim-css-color'
Plug 'https://github.com/ryanoasis/vim-devicons'
set encoding=UTF-8
let g:airline_powerline_fonts = 1

call plug#end()

nnoremap <C-t> :NERDTreeToggle<CR>
nnoremap <C-_> :Commentary<CR>
nnoremap <C-i> :tabnext<CR>