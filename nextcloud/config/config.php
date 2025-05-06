<?php
$CONFIG = array (
  'instanceid' => 'swissairdry' . md5(uniqid(true)),
  'passwordsalt' => '',
  'secret' => '',
  'trusted_domains' => 
  array (
    0 => 'localhost',
    1 => 'localhost:8080',
    2 => 'nextcloud',
  ),
  'datadirectory' => '/var/www/html/data',
  'dbtype' => 'pgsql',
  'dbname' => 'nextcloud',
  'dbhost' => 'postgres',
  'dbport' => '5432',
  'dbtableprefix' => 'oc_',
  'dbuser' => 'postgres',
  'dbpassword' => 'postgres',
  'installed' => true,
  'memcache.local' => '\\OC\\Memcache\\Redis',
  'memcache.distributed' => '\\OC\\Memcache\\Redis',
  'redis' => 
  array (
    'host' => 'redis',
    'port' => 6379,
  ),
  'app_install_overwrite' => 
  array (
    0 => 'diamond',
  ),
  'maintenance' => false,
  'theme' => '',
  'loglevel' => 2,
  'mail_domain' => 'swissairdry.com',
  'mail_from_address' => 'admin',
  'mail_smtpmode' => 'smtp',
  'mail_smtphost' => 'smtp',
  'mail_smtpport' => '25',
  'default_language' => 'de',
  'default_locale' => 'de_DE',
  'default_phone_region' => 'CH',
  'overwrite.cli.url' => 'http://localhost:8080/',
);