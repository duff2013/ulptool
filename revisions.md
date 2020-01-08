><b>Updated (1/8/20 v2.4.2)</b><br>
* Fix readme.md ulpcc example.<br>

><b>Updated (8/20/19 v2.4.1)</b><br>
* Added lcc copyright file.<br>
* Fix grammar and spelling of README.md.<br>
* Fix lcc examples.<br>

><b>Updated (7/14/19 v2.4.0)</b><br>
* Added support for ulpcc c compiler :)<br>
* Cleaned up code.<br>

><b>Updated (2/15/19 v2.3.0)</b><br>
* Fixed flash memory allocation.<br>
* Add custom binary load function("ulptool_load_binary").<br>
* Use python to run the esp32.ld thru the c preprocessor creating an updated esp32_out.ld<br>
* Print ulp memory usage in stdout now.<br>

><b>Updated (2/8/19 v2.2.0)</b><br>
* Fixed compiling of non ulp projects.<br>
* Changed example file name from README.ino to ulp_README.ino.<br>
* All files versions numbers match the global version now.<br>

><b>Updated (2/5/19 v2.1.0)</b><br>
* Now compiles for archived cores. i.e esp32 cores v1.0.0 and v1.0.1<br>
* Changed install procedure, hopefully easier.<br>
* Now use platform.local.txt, no need for user to edit platform.txt anymore.<br>
* Cleaned up prints in Windows<br>

><b>Updated (1/8/19 v2.0.0)</b><br>
* Updated to use the esp32 core installed by the Arduino board manager now since its the preferred way to install now.<br>

><b>Updated (11/20/18 v1.8.2)</b><br>
Updated platform.txt to newest version.<br>

><b>Updated (9/8/18 v1.8.1)</b><br>
* Fix indents.<br>

><b>Updated (9/8/18 v1.8.0)</b><br>
* Now uses cpreprocessor flags from platform.txt instead of being hardcoded.<br>
* Uses argparse now.<br>

><b>Updated (8/17/18 v1.7.0)</b><br>
* Update platform.txt to arduino-esp32 v1.0.0 and ulp assembly compile<br>
* Add comment to increase ulp memory in examples<br>

><b>Updated (8/16/18 v1.6.1)</b><br>
* Added new example sketch from README.md.<br>
* Fixed binutils-esp32ulp download path.<br>

><b>Updated (4/14/18 v1.6.0)</b><br>
* Fixed Windows issue of needing python called explesivly in esp32ulp_build_recipe.py.<br>
* Tested and works with Linux Ubuntu VR on my Mac.<br>
* Tested and works with Windows 7 VR on my Mac.<br>


><b>Updated (4/11/18 v1.5.0)</b><br>
* Fixed a few OS dependent paths, hopefully windows and linux are fully supported now.<br>
* Added MIT license.<br>

><b>Updated (4/8/18 v1.4.0)</b><br>
* Now handles multiple assembly files.<br>
* update examples<br>
* update README.md<br>

><b>Updated (4/5/18 v1.3.0)</b><br>
* fixed a bunch of issues with esp32ulp_build_recipe.py<br>
* update README.md<br>

><b>Updated (4/1/18 v1.2.1)</b><br>
* cleaned up readme<br>

><b>Updated (3/28/18 v1.2.0)</b><br>
* python - should be platform independent now, windows/linux should work, needs testing<br>
* python - fixed security issue with popen shell cmd<br>
* python - close open files correctly before exiting script<br>
* python - handle stderr better<br>
* check spelling<br>

><b>Updated (3/28/18 v1.1.0)</b><br>
* python - On the road to a platform independent script using os.path in esp32ulp_build_recipe.py<br>
* Update readme<br>

><b>Updated (3/27/18 v1.0.1)</b><br>
* python - Update python script, no structural changes just added comments<br>
* Update readme<br>

><b>Updated (3/26/18 v1.0.0)</b><br>
* Initial commit<br>
