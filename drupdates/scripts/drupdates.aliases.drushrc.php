<?php
// Grab the "Global" settings from drupdates
$result = json_decode(exec('python ~/.drush/settings.py'), true);
$path = $result['workingDir']['value'];
$driver = $result['datastoreDriver']['value'];
$user = $result['datastoreSuperUser']['value'];
$pass = $result['datastoreSuperPword']['value'];
$port = $result['datastorePort']['value'];
$host = $result['datastoreHost']['value'];
$webroot = $result['webrootDir']['value'];

// I'm not sure why but if you keep $result populated you get ghost aliases who
// values are the same as the $result array elelment names
$result = array();
$aliases = array();
$dir_handle = new DirectoryIterator($path);
while($dir_handle->valid()) {
  if($dir_handle->isDir() && !$dir_handle->isDot()) {
    $basename = $dir_handle->getBasename();
    $root = $dir_handle->getPathname();
    $root = $webroot = "" ? $root : $root . $webroot;
    $aliases[$basename] = array(
      'uri' => 'http://localhost/' . $basename,
      'root' => $root,
      'databases' => array(
        'default' => array(
          'default' => array(
            'driver' => $driver,
            'username' => $user,
            'password' => $pass,
            'port' => $port,
            'host' => $host,
            'database' => $basename,
          ),
        ),
      ),
    );
  }
  $dir_handle->next();
}
