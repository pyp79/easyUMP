
drop table if exists ITM_SIT_ENRICH;
CREATE TABLE `ITM_SIT_ENRICH` (
	`WRITE_TIME` datetime NOT NULL,
    `SITNAME`        varchar(64) NOT NULL,
    `SIT_DESC`        varchar(128) NOT NULL,
    `THRESHOLD_FLAG`    varchar(64) NOT NULL,
    `CUR_VALUE_FLAG`    varchar(64) NOT NULL,
    `DISPLAY_FLAG`      varchar(64) NOT NULL,
    `N_ComponentType`   varchar(64) NOT NULL,
    `N_ComponentTypeId` varchar(64) NOT NULL,
    `N_Component`       varchar(64) NOT NULL,
    `N_ComponentId`     varchar(64) NOT NULL,
    `N_SubComponent`    varchar(64) NOT NULL,
    `N_SubComponentId`  varchar(64) NOT NULL,
    PRIMARY KEY (`WRITE_TIME`,`SITNAME`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8
