\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{um}[2018/05/01-2019/03/25 v1.2.1 University of Malta, Dissertation/FYP/Thesis Template]


\DeclareOption*{\PassOptionsToClass{\CurrentOption}{memoir}}
\ProcessOptions\relax
\LoadClass[11pt,a4paper,final]{memoir}


%% **************** Packages (Start) *********************

\RequirePackage[utf8]{inputenc}      % Required for inputting international characters
\RequirePackage[T1]{fontenc}         % Output font encoding for international characters
\RequirePackage{mathpazo}            % Use the Palatino font by default
\RequirePackage[english]{babel}      % Load babel if you're unsure about the default language - mostly to be safe
\RequirePackage{xcolor}              % For named colors
\RequirePackage{eso-pic}                 % required to place huge uni logo at the back - on title page
\RequirePackage[pdftex]{graphicx}    % For pictures
\RequirePackage{amssymb}             % At least, for black squares in bullet list
\RequirePackage[pdfusetitle]{hyperref}             % For hyperreferences
\RequirePackage[authoryear,semicolon,sort]{natbib} % for (Ebejer, 2012; Alba, 2013) kind of references; removed 'square' option after viva examination comments

\RequirePackage{longtable}           % For very long tables
\RequirePackage{pdflscape}			 % For landscape tables (instead of portrait)

\usepackage[defaultsans]{lato}		 % Sans font to use
\usepackage[printonlyused,withpage]{acronym}
\usepackage{geometry}
\usepackage{multicol}
\usepackage[framed,numbered]{matlab-prettifier}
\usepackage{amsmath}
\usepackage{hyperref}
\usepackage{framed}

%% ****************** Packages (End) *********************


%% ************ UM Definitions (Start) *****************

\definecolor{OxfordBlue}{rgb}{0,0.106,0.329}   % Color
\definecolor{sarstemred}{rgb}{0.73,0.09,0.19}   % Theme Color

% Setup choosen University of Malta crest/logo
\def\logo{{\includegraphics[width=50mm]{images/sarstemlogo.png}}}
% hi hello
%\def\logo2{{\includegraphics[width=50mm]{images/exouls2.png}}}
% The year and term the thesis is submitted 
\def\degreedate#1{\gdef\@degreedate{#1}}
% The full (unabbreviated) name of the degree
\def\degree#1{\gdef\@degree{#1}}
% The name of your supervisor
\def\supervisor#1{\gdef\@supervisor{#1}}
% The name of your co-supervisor
\def\department#1{\gdef\@department{#1}}
% The name of your faculty
\def\faculty#1{\gdef\@faculty{#1}}
% The name of your faculty
\def\subjectcode#1{\gdef\@subjectcode{#1}}
% The document type, e.g. a dissertation or a thesis
\def\doctype#1{\gdef\@doctype{#1}}
\def\authorID#1{\gdef\@authorID{#1}}

%% ************* UM Definitions (End) ******************


%% ************ Document Options (Start) *****************

\OnehalfSpacing                                  % One and a half line spacing

\setlength{\headsep}{1.2cm}                      % Add space between the header and text

\nouppercaseheads								 % Don't convert titles to Uppercase
\makepagestyle{umpage}

												 % This travesty is due to a bug in memoir, see https://tex.stackexchange.com/questions/468922/oneside-in-memoir-causing-header-trouble
\makeevenhead{umpage}{\color{gray}\sffamily\small\leftmark}{}{\color{gray}\sffamily\small\rightmark}
\makeoddhead{umpage}{\color{gray}\sffamily\small\leftmark}{}{\color{gray}\sffamily\small\rightmark}
\makeevenfoot{umpage}{}{\thepage}{}  			 % UM pagestyle, put page at bottom
\makeoddfoot{umpage}{}{\thepage}{}
\makeheadfootruleprefix{umpage}{\color{gray}}{}
\makeheadrule{umpage}{\textwidth}{\normalrulethickness}
\makepsmarks{umpage}{%
	\createmark{chapter}{left}{shownumber}{\@chapapp\ }{. \ }
	\createmark{section}{right}{shownumber}{}{. \ }
}


\setlrmarginsandblock{3.7cm}{2.5cm}{*}           % Set the page margins (for one and two sided docs) 
\checkandfixthelayout                            % Put layout into effect

\graphicspath{{./images/}}                       % Where to look for images (paths) ...
\DeclareGraphicsExtensions{.pdf,.jpeg,.png,.jpg} % Graphics extensions to load

\makechapterstyle{ell}{%
  \chapterstyle{default}
  \renewcommand*{\chapnumfont}{\normalfont\HUGE\sffamily}
  \renewcommand*{\chaptitlefont}{\normalfont\huge\sffamily}
  \settowidth{\chapindent}{\chapnumfont 111}
  \renewcommand*{\chapterheadstart}{\begingroup
    \vspace*{0cm}%
    \begin{adjustwidth}{}{0cm}%
    \hrulefill
    \smash{\rule{0.4pt}{0cm}}
    \end{adjustwidth}\endgroup}
  \renewcommand*{\printchaptername}{}
  \renewcommand*{\chapternamenum}{}
  \renewcommand*{\printchapternum}{%
    \begin{adjustwidth}{}{}
    \hfill
    \raisebox{10mm}[0pt][0pt]{\chapnumfont \thechapter}%
                              \hspace*{1em}
    \end{adjustwidth}\vspace*{-3.2\onelineskip}}
  \renewcommand*{\printchaptertitle}[1]{%
    \vskip\onelineskip
    \centering {\chaptitlefont ##1}\par\vspace*{0.1cm}\hrulefill\nobreak}
}
    
\chapterstyle{ell} % how to draw the different chapter headings

\renewcommand*{\chapnumfont}{\sffamily\HUGE\bfseries\color{sarstemred}}  % Chapter titles should be normal
\renewcommand*{\chaptitlefont}{\sffamily\HUGE\bfseries\color{sarstemred}}
\setsecheadstyle{\sffamily\LARGE\bfseries\color{sarstemred}}% Set \section style
\setsubsecheadstyle{\sffamily\Large\color{sarstemred}}% Set \subsection style
\setsubsubsecheadstyle{\sffamily\large\color{sarstemred}}% Set \subsection style
\setsecnumformat{\csname the#1\endcsname\enskip{\color{gray}\textbar}\enskip}

\newsubfloat{figure} % declares a new subfloat element which allows to use \subbottom commands

\renewcommand{\labelitemi}{\color{sarstemred}\scriptsize$\blacksquare$}

\addto{\captionsenglish}{\renewcommand{\bibname}{References}} % because we are using babel we need this
                                                              % instead of just redefining bibname
\setlength{\bibitemsep}{\onelineskip}

\newcommand{\ra}[1]{\renewcommand{\arraystretch}{#1}} % to set array stretch within tables

\hypersetup{%
    colorlinks=false,
%    linkcolor=sarstemred,
%    citecolor=sarstemred,
%    urlcolor=sarstemred,
%    filecolor=magenta, 
    pdfborder={0 0 0},    
}

\feetbelowfloat % we want the footnotes below floats, not wierdly above

\setsecnumdepth{subsubsection}  % three level depth - chapter, section, subsection, subsubsection
\settocdepth{subsection}

\renewcommand*{\cftappendixname}{Appendix\space}
\newcommand{\removelinebreaks}[1]{%
	\begingroup\def\\{ }#1\endgroup}

%% ************* Document Options (End) ******************



%% *************** Environments (Start) ******************

%% *** Title Page (Start) ***
% background image
% taken from http://tug.org/pracjourn/2008-1/mori/mori.pdf
\newcommand\AlCentroPagina[1]{%
\AddToShipoutPicture*{\AtPageCenter{%
\makebox(0,-50){\includegraphics[width=0.5\paperwidth]{#1}}}}}

% The front page
\renewcommand{\maketitle}
{\begingroup
\newgeometry{left=1cm,right=2cm,top=4cm,bottom=3cm}
%\AlCentroPagina{umlogo_crest_gray}
\parbox[b][0.95\textheight][t]{0.26\textwidth}{\raggedleft\logo} %% this 0.95 is important, otherwise page overflows in next page
%\parbox[b][0.75\textheight][t]{0.27\textwidth}{\raggedleft\includegraphics[width=50mm]{images/exouls2.png}}
\hspace*{2ex}
\textcolor{sarstemred}{\rule{2.5pt}{0.95\textheight}}
\hspace*{2ex}
\parbox[b][0.95\textheight][t]{0.8\textwidth}{
    \setlength{\parindent}{0pt}
    %%\fontfamily{pag}\selectfont
    \sffamily
    {\Huge\bfseries{\begin{Spacing}{1.15}\textcolor{sarstemred}{\@title}\end{Spacing}}}
    \vspace*{2ex}
    \vspace*{3cm}
    {\LARGE\bfseries \textsc{\@author}} \\[1cm]
    {\Large Supervisor: \textbf{\@supervisor}}\\[4.25cm]
    {\large \@department} \\[1ex]
    {\large \@faculty} \\[1ex]
    {\large Society for Academic Research in STEM} \\
    \vfill
    {\bfseries Submitted: \@degreedate}\\[0.8cm]
	\parbox[t]{0.80\linewidth}{\footnotesize {This \@doctype\ has been submitted in fulfilment of progress requirements for the 8-week \@degree} summer research fellowship program at SARSTEM.}    
}
\thispagestyle{empty}
\clearpage
\restoregeometry
\endgroup}

%% *** Title Page (End) ***

\newenvironment{dedication}
  {\clearpage           % we want a new page
   \newgeometry{left=3cm,right=1.7cm}
   \thispagestyle{empty}% no header and footer
   \vspace*{\stretch{2}}% some space at the top 
   \itshape             % the text is in italics
   \raggedleft          % flush to the right margin
   \textcolor{sarstemred}
  }
  {\par % end the paragraph
   \vspace{\stretch{3}} % space at bottom is three times that at the top
   \restoregeometry\clearpage
  }       
  
 \newenvironment{acknowledgements}
{\renewcommand{\abstractname}{\huge\bfseries\sffamily\textcolor{sarstemred}{Acknowledgements}}\abstract}
{\endabstract\clearpage}
       
\addto{\captionsenglish}{\renewcommand{\abstractname}{\huge\bfseries\sffamily\textcolor{sarstemred}{Abstract}}}


\newenvironment{teammates}
{\renewcommand{\abstractname}{\huge\bfseries\sffamily\textcolor{sarstemred}{Team Members}}\abstract}
{\endabstract\clearpage}
       
\addto{\captionsenglish}{\renewcommand{\abstractname}{\huge\bfseries\sffamily\textcolor{sarstemred}{Abstract}}}

       

%%\renewenvironment{abstract}
%%{\begin{alwayssingle} \thispagestyle{empty}
%%\begin{center}
%%\vspace*{0.5cm}
%%{\large \bfseries \textcolor{sarstemred}{Abstract}}
%%\end{center}
%%\singlespacing\enlargethispage{\baselineskip}}
%%{\end{alwayssingle}}

%%{\cleardoublepage\newgeometry{right=1.3cm,top=2.4cm,bottom=2cm}\pagestyle{empty}\begin{center}\bfseries\large\textcolor{OxfordBlue}\abstractname\end{center}\normalsize\onehalfspacing\begin{quotation}}{\end{quotation}\restoregeometry\cleardoublepage}

%% **************** Environments (End) *******************