<?php
declare(strict_types=1);

/**
 * @copyright Copyright (c) 2025 Swiss Air Dry Team <info@swissairdry.com>
 *
 * @license AGPL-3.0-or-later
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

return [
    'routes' => [
        // Seiten-Routen
        ['name' => 'page#index', 'url' => '/', 'verb' => 'GET'],
        ['name' => 'page#dashboard', 'url' => '/dashboard', 'verb' => 'GET'],
        ['name' => 'page#devices', 'url' => '/devices', 'verb' => 'GET'],
        ['name' => 'page#device_detail', 'url' => '/devices/{id}', 'verb' => 'GET'],
        ['name' => 'page#map', 'url' => '/map', 'verb' => 'GET'],
        ['name' => 'page#settings', 'url' => '/settings', 'verb' => 'GET'],
        
        // API-Routen
        ['name' => 'api#get_devices', 'url' => '/api/devices', 'verb' => 'GET'],
        ['name' => 'api#get_device', 'url' => '/api/devices/{id}', 'verb' => 'GET'],
        ['name' => 'api#update_device', 'url' => '/api/devices/{id}', 'verb' => 'PUT'],
        ['name' => 'api#send_command', 'url' => '/api/devices/{id}/command', 'verb' => 'POST'],
        ['name' => 'api#get_device_data', 'url' => '/api/devices/{id}/data', 'verb' => 'GET'],
        ['name' => 'api#get_device_location', 'url' => '/api/devices/{id}/location', 'verb' => 'GET'],
        
        // MQTT-Proxy-Routen
        ['name' => 'mqtt#publish', 'url' => '/api/mqtt/publish', 'verb' => 'POST'],
        ['name' => 'mqtt#status', 'url' => '/api/mqtt/status', 'verb' => 'GET'],
        
        // Einstellungs-Routen
        ['name' => 'settings#get', 'url' => '/api/settings', 'verb' => 'GET'],
        ['name' => 'settings#update', 'url' => '/api/settings', 'verb' => 'PUT'],
    ]
];