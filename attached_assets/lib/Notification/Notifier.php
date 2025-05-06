<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\Notification;

use OCP\IURLGenerator;
use OCP\L10N\IFactory;
use OCP\Notification\INotification;
use OCP\Notification\INotifier;

class Notifier implements INotifier {
    /** @var IFactory */
    private $l10nFactory;
    
    /** @var IURLGenerator */
    private $urlGenerator;

    public function __construct(IFactory $l10nFactory, IURLGenerator $urlGenerator) {
        $this->l10nFactory = $l10nFactory;
        $this->urlGenerator = $urlGenerator;
    }

    /**
     * Identifier of the notifier, only use [a-z0-9_]
     */
    public function getID(): string {
        return 'swissairdry';
    }

    /**
     * Human readable name describing the notifier
     */
    public function getName(): string {
        return $this->l10nFactory->get('swissairdry')->t('Swiss Air Dry');
    }

    /**
     * Bereitet eine Benachrichtigung für die Anzeige auf
     *
     * @param INotification $notification Die zu präparierende Benachrichtigung
     * @param string $languageCode Die Sprache, in der die Benachrichtigung angezeigt werden soll
     * @return INotification Die präparierte Benachrichtigung
     * @throws \InvalidArgumentException Wenn die Benachrichtigung nicht präpariert werden kann
     */
    public function prepare(INotification $notification, string $languageCode): INotification {
        if ($notification->getApp() !== 'swissairdry') {
            throw new \InvalidArgumentException('Falsche App');
        }

        // Sprache laden
        $l = $this->l10nFactory->get('swissairdry', $languageCode);

        // Verschiedene Benachrichtigungstypen behandeln
        switch ($notification->getSubject()) {
            case 'device_offline':
                $params = $notification->getSubjectParameters();
                $deviceName = $params['deviceName'] ?? $params['deviceId'];
                
                $notification->setIcon($this->urlGenerator->imagePath('swissairdry', 'swissairdry.svg'));
                $notification->setParsedSubject(
                    $l->t('Gerät offline: %s', [$deviceName])
                );
                
                if ($notification->getMessage() === 'device_offline_details') {
                    $messageParams = $notification->getMessageParameters();
                    $timeSince = $messageParams['timeSince'] ?? '';
                    
                    $notification->setParsedMessage(
                        $l->t('Das Gerät ist seit %s nicht mehr erreichbar.', [$timeSince])
                    );
                }
                
                // Link zum Gerät hinzufügen
                $deviceId = $params['deviceId'];
                $notification->setLink($this->urlGenerator->linkToRoute(
                    'swissairdry.page.device_detail',
                    ['id' => $deviceId]
                ));
                
                return $notification;
                
            case 'device_alert':
                $params = $notification->getSubjectParameters();
                $deviceName = $params['deviceName'] ?? $params['deviceId'];
                $alertType = $params['alertType'] ?? 'unknown';
                
                $notification->setIcon($this->urlGenerator->imagePath('swissairdry', 'swissairdry.svg'));
                
                switch ($alertType) {
                    case 'temperature':
                        $notification->setParsedSubject(
                            $l->t('Temperaturwarnung: %s', [$deviceName])
                        );
                        break;
                    case 'humidity':
                        $notification->setParsedSubject(
                            $l->t('Luftfeuchtigkeitswarnung: %s', [$deviceName])
                        );
                        break;
                    case 'pressure':
                        $notification->setParsedSubject(
                            $l->t('Druckwarnung: %s', [$deviceName])
                        );
                        break;
                    case 'power':
                        $notification->setParsedSubject(
                            $l->t('Stromversorgungswarnung: %s', [$deviceName])
                        );
                        break;
                    default:
                        $notification->setParsedSubject(
                            $l->t('Warnung für Gerät: %s', [$deviceName])
                        );
                        break;
                }
                
                if ($notification->getMessage() === 'device_alert_details') {
                    $messageParams = $notification->getMessageParameters();
                    $alertValue = $messageParams['alertValue'] ?? '';
                    $threshold = $messageParams['threshold'] ?? '';
                    
                    switch ($alertType) {
                        case 'temperature':
                            $notification->setParsedMessage(
                                $l->t('Die Temperatur (%s°C) hat den Schwellenwert (%s°C) überschritten.', [$alertValue, $threshold])
                            );
                            break;
                        case 'humidity':
                            $notification->setParsedMessage(
                                $l->t('Die Luftfeuchtigkeit (%s%%) hat den Schwellenwert (%s%%) überschritten.', [$alertValue, $threshold])
                            );
                            break;
                        case 'pressure':
                            $notification->setParsedMessage(
                                $l->t('Der Druck (%s hPa) hat den Schwellenwert (%s hPa) überschritten.', [$alertValue, $threshold])
                            );
                            break;
                        case 'power':
                            $notification->setParsedMessage(
                                $l->t('Die Leistungsaufnahme (%s W) hat den Schwellenwert (%s W) überschritten.', [$alertValue, $threshold])
                            );
                            break;
                        default:
                            $notification->setParsedMessage(
                                $l->t('Ein Sensorwert hat den konfigurierten Schwellenwert überschritten.')
                            );
                            break;
                    }
                }
                
                // Link zum Gerät hinzufügen
                $deviceId = $params['deviceId'];
                $notification->setLink($this->urlGenerator->linkToRoute(
                    'swissairdry.page.device_detail',
                    ['id' => $deviceId]
                ));
                
                return $notification;
                
            case 'firmware_update':
                $params = $notification->getSubjectParameters();
                $deviceName = $params['deviceName'] ?? $params['deviceId'];
                
                $notification->setIcon($this->urlGenerator->imagePath('swissairdry', 'swissairdry.svg'));
                $notification->setParsedSubject(
                    $l->t('Firmware-Update verfügbar: %s', [$deviceName])
                );
                
                if ($notification->getMessage() === 'firmware_update_details') {
                    $messageParams = $notification->getMessageParameters();
                    $currentVersion = $messageParams['currentVersion'] ?? '';
                    $newVersion = $messageParams['newVersion'] ?? '';
                    
                    $notification->setParsedMessage(
                        $l->t('Eine neue Firmware-Version ist verfügbar: %s (aktuell: %s).', [$newVersion, $currentVersion])
                    );
                }
                
                // Link zum Gerät hinzufügen
                $deviceId = $params['deviceId'];
                $notification->setLink($this->urlGenerator->linkToRoute(
                    'swissairdry.page.device_detail',
                    ['id' => $deviceId]
                ));
                
                return $notification;
                
            default:
                // Unbekannter Benachrichtigungstyp
                throw new \InvalidArgumentException('Unbekannter Benachrichtigungstyp');
        }
    }
}