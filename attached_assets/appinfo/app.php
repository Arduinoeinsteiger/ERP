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

// Diese Datei wird bei der App-Initialisierung geladen

namespace OCA\SwissAirDry\AppInfo;

use OCP\AppFramework\App;

$app = new App('swissairdry');
$container = $app->getContainer();

// Scripts und Styles für Nextcloud Navigation
$eventDispatcher = $container->getServer()->getEventDispatcher();
$eventDispatcher->addListener('OCA\Files::loadAdditionalScripts', function() {
    script('swissairdry', 'swissairdry-files');
});

// Navigation-Eintrag für Nextcloud Hauptnavigation
$container->getServer()->getNavigationManager()->add(function () use ($container) {
    $urlGenerator = $container->getServer()->getURLGenerator();
    $l10n = $container->getServer()->getL10N('swissairdry');
    return [
        'id' => 'swissairdry',
        'order' => 10,
        'href' => $urlGenerator->linkToRoute('swissairdry.page.index'),
        'icon' => $urlGenerator->imagePath('swissairdry', 'swissairdry.svg'),
        'name' => $l10n->t('Swiss Air Dry'),
    ];
});