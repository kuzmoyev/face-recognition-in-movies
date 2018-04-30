%% LaTeX template class for technical report
%% for subject MVI in Czech Technical University in Prague (CTU)
%%
%% (c) 2008 Vit Zyka
%%
%% History:
%% 0.1 2008-09-21 new for NRP
%% 0.2 2008-11-12 href for email, unicode in hyperref; tolerance; microtype; cmap
%%   \texorpdfstring
%% 0.3 2018-02-12 update for purposes of MI-MVI

\typeout{Class mvi-report v0.3, 2018-02-12, Martin Slapak, Vit Zyka}

%% Options...
\newif\ifCzech

\DeclareOption{czech}{\Czechtrue}
\ProcessOptions

\LoadClass[a4paper,normalheadings]{scrartcl}

%% Dimensions...
\setlength{\columnsep}{10mm}

\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.9}
\renewcommand{\dbltopfraction}{0.9}
\renewcommand{\textfraction}{0}
\setcounter{topnumber}{4}
\setcounter{bottomnumber}{4}
\setcounter{totalnumber}{4}
\setcounter{dbltopnumber}{4}

\tolerance=300

%% Packages...
\RequirePackage{ifpdf}
\ifCzech
  \RequirePackage[czech]{babel}
\fi
\RequirePackage{lmodern}
\RequirePackage{cmap}
\usepackage[T1]{fontenc}
%\usepackage{ae,aecompl} 
\usepackage[left=15mm,right=15mm,top=18mm,bottom=20mm,footskip=10mm]{geometry}
\ifpdf
  \RequirePackage[pdftex]{graphicx}
  \RequirePackage[pdftex]{color}
\else
  \RequirePackage{graphicx}
  \RequirePackage{color}
\fi
\RequirePackage[pdfpagemode=UseNone,pdfborder=0 0 0,unicode]{hyperref}
\RequirePackage{mflogo}
\RequirePackage{natbib}
\RequirePackage{microtype}

%% Title...
\newtoks\MVIemail        \def\email#1{\MVIemail={#1}}
\newtoks\MVIaffiliation  \def\affiliation#1{\MVIaffiliation={#1}}

\def\affiliationFont{\normalfont\fontsize{12pt}{14pt}\selectfont}

\AtBeginDocument{%
  \expandafter\author\expandafter{%
    \@author\\[4pt]\affiliationFont
    \def\\{\crcr\affiliationFont}\the\MVIaffiliation\\
    \href{mailto:\the\MVIemail}{\affiliationFont\the\MVIemail}}%
  \expandafter\date\expandafter{\expandafter\affiliationFont\@date}%
}

\let\maketitleOrig=\maketitle
\def\maketitle{\@ifnextchar[{\domaketitle}{\domaketitle[]}}
\def\domaketitle[#1]{%
  \twocolumn[\vskip-2.0cm\maketitleOrig\begin{quotation}#1\end{quotation}\vskip-1.0cm]%
}
%\bigskip

% pokus o usetreni mista v \paragraph
\let\paragraphOrig=\paragraph
\renewcommand\paragraph{
\@startsection
{paragraph}       % the name
{4}               % the level
{\z@}             % the indent
{1.5ex \@plus1ex \@minus.2ex}  % the before skip
{-1em}                          % the after skip
{\normalfont\normalsize\bfseries} % the style
}                                
\renewcommand{\baselinestretch}{1}
\setlength{\parskip}{-0.3ex}

%% Bibliography...
% citace dle abecedy
\bibliographystyle{plain}
% citace dle poradi, ale nevejde se to
%\bibliographystyle{is-unsrt}
% citace dle poradi, ale vejde se to ;-)
%\bibliographystyle{unsrt}
 
%% Misc...
\def\CONTEXT{\texorpdfstring{Con\kern-.1em\TeX{}t}{ConTeXt}}
\def\MetaPost{\texorpdfstring{\MP}{MetaPost}}

\endinput


