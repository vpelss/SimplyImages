#!/usr/bin/perl -w

require "SimplyImages.cfg";

print "Content-type: text/html\n\n";

%in = &parse_form();

#get template.html
open (MAIN, "templates/template.html");
$DisplayTemplate = join ('' , <MAIN>);
close MAIN;

#directory
if ($in{dir})
     {
     $tr = '';
     $td = '';
     $maintablecount = 0;

     $in{dir} =~ s/\/$//g; #remove trailing /

     #get directory list
     opendir(DIR, "$in{dir}") || die "can't opendir $in{dir}: $!";
     @directories = sort grep {not (/\./) && -d "$in{dir}/$_"} readdir(DIR);
     closedir DIR;

     #create $directories
     foreach $cats(@directories)
              {
              $fil = $cats;
              $fil =~ s/\.\w+//;
              $fil =~ s/_/ /g;

              #get files in dir
              opendir(DIR, "$in{dir}/$cats") || die "can't opendir $in{dir}/$cats: $!";
              @images = grep {-f "$in{dir}/$cats/$_"} readdir(DIR);
              closedir DIR;

              $randlength = @images;
              $randimg = $images[rand $randlength];

              $td = qq|
              $td
              <td ID='DirectoryTD'>
              <a href=\"?dir=$in{dir}/&cat=$cats"><img src=\"$in{dir}/$cats/$randimg\" ID='DirIMG' height=$thumbnailheight border=0><br><DIV ID='DirDIV'>$fil</DIV></a>
              </td>
              |;

               $maintablecount++;
               if ($maintablecount == $columns)
                     {
                     $directorytable = qq|$directorytable <table ID='DirectoryTable'><tr ID='DirTR'>$td</tr></table><br>|;;
                     $td = '';
                     $maintablecount = 0;
                     }
                }
     if ($maintablecount < $columns) {$directorytable = qq|$directorytable <table ID='DirectoryTable'><tr ID='DirTR'>$td</tr></table><br>|;}
     $DirectoryTitle2 = $DirectoryTitle;
     };

if ($in{cat})
     {
     $tr = '';
     $td = '';
     $maintablecount = 0;

     #get files list
     opendir(DIR, "$in{dir}/$in{cat}") || die "can't opendir $in{dir}/$in{cat}: $!";
     @files = sort grep {-f "$in{dir}/$in{cat}/$_"} readdir(DIR);
     closedir DIR;

     #files
     foreach $file(@files)
              {
              $fil = $file;
              $fil =~ s/\.\w+//;
              $fil =~ s/_/ /g;

              $td = qq|
              $td
              <td ID='ImagesTD'>
              <a href="?dir=$in{dir}&cat=$in{cat}&image=$file"><img src="$in{dir}/$in{'cat'}/$file" ID='ImagesIMG' height=$thumbnailheight border=0><br><DIV ID='ImagesDIV'>$fil</DIV></a>
              </td>
              |;

               $maintablecount++;
               if ($maintablecount == $columns)
                     {
                     $imagestable = qq|$imagestable <table ID='ImagesTable'><tr ID='ImageTR'>$td</tr></table>|;
                     $td = '';
                     $maintablecount = 0;
                     }
                }
     if ($maintablecount < $columns) {$imagestable = qq|$imagestable <table ID='ImagesTable'><tr ID='ImageTR'>$td</tr></table>|;}
     $ImagesTitle2 = $ImagesTitle;
     };

#image
if ($in{image})
     {
     $fil = $in{image};
     $fil =~ s/\.\w+//;
     $fil =~ s/_/ /g;

     $imagetable = qq|
     <table>
     <td ID='ImageTD'>
              <img src='$in{dir}/$in{cat}/$in{image}'>
              <br>
              <DIV ID='ImageDIV'>
              $fil
              </DIV>
              </td>
     </table>
     |;

     $ImageTitle2 = $ImageTitle;
     };

$DisplayTemplate =~ s/\<\%directories\%\>/$directorytable/g;
$DisplayTemplate =~ s/\<\%DirectoryTitle\%\>/$DirectoryTitle2/g;

$DisplayTemplate =~ s/\<\%images\%\>/$imagestable/g;
$DisplayTemplate =~ s/\<\%ImagesTitle\%\>/$ImagesTitle2/g;

$DisplayTemplate =~ s/\<\%image\%\>/$imagetable/g;
$DisplayTemplate =~ s/\<\%ImageTitle\%\>/$ImageTitle2/g;

print "$DisplayTemplate";

sub parse_form {
# --------------------------------------------------------
# Parses the form input and returns a hash with all the name
# value pairs. Removes SSI and any field with "---" as a value
# (as this denotes an empty SELECT field.

        my (@pairs, %in);
        my ($buffer, $pair, $name, $value);

        if ($ENV{'REQUEST_METHOD'} eq 'GET') {
                @pairs = split(/&/, $ENV{'QUERY_STRING'});
        }
        elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
                read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
                 @pairs = split(/&/, $buffer);
        }
        else {
                &cgierr ("This script must be called from the Web\nusing either GET or POST requests\n\n");
        }
        PAIR: foreach $pair (@pairs) {
                ($name, $value) = split(/=/, $pair);

                $name =~ tr/+/ /;
                $name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

                $value =~ tr/+/ /;
                $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

                $value =~ s/<!--(.|\n)*-->//g;                          # Remove SSI.
                if ($value eq "---") { next PAIR; }                  # This is used as a default choice for select lists and is ignored.
                (exists $in{$name}) ?
                        ($in{$name} .= "~~$value") :              # If we have multiple select, then we tack on
                        ($in{$name}  = $value);                                  # using the ~~ as a seperator.
        }
        return %in;
}