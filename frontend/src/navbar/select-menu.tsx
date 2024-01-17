import { Button, Menu, Popover } from "@blueprintjs/core";
import { SelectMenuItem } from "./select-menu-item";
import { MenuType, useCurrentMenuType } from "../common/menu-type";
import { getMenuProps } from "./menu-props";

export function SelectMenu() {
    const currentMenuType = useCurrentMenuType();

    const currentMenuButton = (
        <Button
            {...getMenuProps(currentMenuType)}
            rightIcon="caret-down"
            intent="primary"
            alignText="left"
            minimal
        />
    );

    const currentMenuTypes = Object.values(MenuType).filter(
        (menuType) => menuType !== currentMenuType
    );

    const menuItems = currentMenuTypes.map((menuType) => (
        <SelectMenuItem
            key={menuType}
            {...getMenuProps(menuType)}
            menuType={menuType}
        />
    ));

    const menu = <Menu>{menuItems}</Menu>;

    return (
        <Popover content={menu} minimal placement="bottom-end">
            {currentMenuButton}
        </Popover>
    );
}
