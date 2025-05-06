<ul>
    <li>
        <a href="<?php p(\OC::$server->getURLGenerator()->linkToRoute('swissairdry.page.index')); ?>"
           class="nav-icon-dashboard svg">
            <?php p($l->t('Dashboard')); ?>
        </a>
    </li>
    <li>
        <a href="<?php p(\OC::$server->getURLGenerator()->linkToRoute('swissairdry.page.devices')); ?>"
           class="nav-icon-devices svg">
            <?php p($l->t('Geräte')); ?>
        </a>
    </li>
    <li>
        <a href="<?php p(\OC::$server->getURLGenerator()->linkToRoute('swissairdry.page.map')); ?>"
           class="nav-icon-map svg">
            <?php p($l->t('Karte')); ?>
        </a>
    </li>
    <li>
        <a href="<?php p(\OC::$server->getURLGenerator()->linkToRoute('swissairdry.page.settings')); ?>"
           class="nav-icon-settings svg">
            <?php p($l->t('Einstellungen')); ?>
        </a>
    </li>
</ul>