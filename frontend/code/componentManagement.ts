import { BuildFailedComponent } from './components/buildFailed';
import { ButtonComponent } from './components/button';
import { CalendarComponent } from './components/calendar';
import { CardComponent } from './components/card';
import { CheckboxComponent } from './components/checkbox';
import { ClassContainerComponent } from './components/classContainer';
import { CodeBlockComponent } from './components/codeBlock';
import { CodeExplorerComponent } from './components/codeExplorer';
import { ColorPickerComponent } from './components/colorPicker';
import { ColumnComponent, RowComponent } from './components/linearContainers';
import { ComponentBase, ComponentState } from './components/componentBase';
import { ComponentId } from './dataModels';
import { ComponentTreeComponent } from './components/componentTree';
import { CustomListItemComponent } from './components/customListItem';
import { DevToolsConnectorComponent } from './components/devToolsConnector';
import { DrawerComponent } from './components/drawer';
import { DropdownComponent } from './components/dropdown';
import { FlowComponent as FlowContainerComponent } from './components/flowContainer';
import { FundamentalRootComponent } from './components/fundamentalRootComponent';
import { GridComponent } from './components/grid';
import { HeadingListItemComponent } from './components/headingListItem';
import { HtmlComponent } from './components/html';
import { IconComponent } from './components/icon';
import { ImageComponent } from './components/image';
import { KeyEventListenerComponent } from './components/keyEventListener';
import { LayoutDisplayComponent } from './components/layoutDisplay';
import { LinkComponent } from './components/link';
import { ListViewComponent } from './components/listView';
import { MarkdownComponent } from './components/markdown';
import { MediaPlayerComponent } from './components/mediaPlayer';
import { MouseEventListenerComponent } from './components/mouseEventListener';
import { MultiLineTextInputComponent } from './components/multiLineTextInput';
import { NodeInputComponent } from './components/nodeInput';
import { NodeOutputComponent } from './components/nodeOutput';
import { OverlayComponent } from './components/overlay';
import { PlaceholderComponent } from './components/placeholder';
import { PlotComponent } from './components/plot';
import { PopupComponent } from './components/popup';
import { ProgressBarComponent } from './components/progressBar';
import { ProgressCircleComponent } from './components/progressCircle';
import { RectangleComponent } from './components/rectangle';
import { reprElement, scrollToUrlFragment } from './utils';
import { RevealerComponent } from './components/revealer';
import { ScrollTargetComponent } from './components/scrollTarget';
import { SeparatorComponent } from './components/separator';
import { SeparatorListItemComponent } from './components/separatorListItem';
import { SliderComponent } from './components/slider';
import { SlideshowComponent } from './components/slideshow';
import { StackComponent } from './components/stack';
import { SwitchComponent } from './components/switch';
import { SwitcherBarComponent } from './components/switcherBar';
import { SwitcherComponent } from './components/switcher';
import { TableComponent } from './components/table';
import { TextComponent } from './components/text';
import { TextInputComponent } from './components/textInput';
import { ThemeContextSwitcherComponent } from './components/themeContextSwitcher';
import { TooltipComponent } from './components/tooltip';

const COMPONENT_CLASSES = {
    'BuildFailed-builtin': BuildFailedComponent,
    'Button-builtin': ButtonComponent,
    'Calendar-builtin': CalendarComponent,
    'Card-builtin': CardComponent,
    'Checkbox-builtin': CheckboxComponent,
    'ClassContainer-builtin': ClassContainerComponent,
    'CodeBlock-builtin': CodeBlockComponent,
    'CodeExplorer-builtin': CodeExplorerComponent,
    'ColorPicker-builtin': ColorPickerComponent,
    'Column-builtin': ColumnComponent,
    'ComponentTree-builtin': ComponentTreeComponent,
    'CustomListItem-builtin': CustomListItemComponent,
    'DevToolsConnector-builtin': DevToolsConnectorComponent,
    'Drawer-builtin': DrawerComponent,
    'Dropdown-builtin': DropdownComponent,
    'FlowContainer-builtin': FlowContainerComponent,
    'FundamentalRootComponent-builtin': FundamentalRootComponent,
    'Grid-builtin': GridComponent,
    'HeadingListItem-builtin': HeadingListItemComponent,
    'Html-builtin': HtmlComponent,
    'Icon-builtin': IconComponent,
    'Image-builtin': ImageComponent,
    'KeyEventListener-builtin': KeyEventListenerComponent,
    'LayoutDisplay-builtin': LayoutDisplayComponent,
    'Link-builtin': LinkComponent,
    'ListView-builtin': ListViewComponent,
    'Markdown-builtin': MarkdownComponent,
    'MediaPlayer-builtin': MediaPlayerComponent,
    'MouseEventListener-builtin': MouseEventListenerComponent,
    'MultiLineTextInput-builtin': MultiLineTextInputComponent,
    'NodeInput-builtin': NodeInputComponent,
    'NodeOutput-builtin': NodeOutputComponent,
    'Overlay-builtin': OverlayComponent,
    'Plot-builtin': PlotComponent,
    'Popup-builtin': PopupComponent,
    'ProgressBar-builtin': ProgressBarComponent,
    'ProgressCircle-builtin': ProgressCircleComponent,
    'Rectangle-builtin': RectangleComponent,
    'Revealer-builtin': RevealerComponent,
    'Row-builtin': RowComponent,
    'ScrollTarget-builtin': ScrollTargetComponent,
    'Separator-builtin': SeparatorComponent,
    'SeparatorListItem-builtin': SeparatorListItemComponent,
    'Slider-builtin': SliderComponent,
    'Slideshow-builtin': SlideshowComponent,
    'Stack-builtin': StackComponent,
    'Switch-builtin': SwitchComponent,
    'Switcher-builtin': SwitcherComponent,
    'SwitcherBar-builtin': SwitcherBarComponent,
    'Table-builtin': TableComponent,
    'Text-builtin': TextComponent,
    'TextInput-builtin': TextInputComponent,
    'ThemeContextSwitcher-builtin': ThemeContextSwitcherComponent,
    'Tooltip-builtin': TooltipComponent,
    Placeholder: PlaceholderComponent,
};

globalThis.COMPONENT_CLASSES = COMPONENT_CLASSES;

export const componentsById: { [id: ComponentId]: ComponentBase | undefined } =
    {};

export const componentsByElement = new Map<HTMLElement, ComponentBase>();

export function getRootComponent(): FundamentalRootComponent {
    let rootComponent = componentsByElement.get(document.body);

    if (rootComponent === undefined) {
        throw new Error('There is no root component yet');
    }

    return rootComponent as FundamentalRootComponent;
}

export function getComponentByElement(element: Element): ComponentBase {
    let instance = tryGetComponentByElement(element);

    if (instance === null) {
        // Just displaying the element itself isn't quite enough information for
        // debugging. We'll go up the tree until we find an element that belongs
        // to a component, and include that in the error message.
        let elem: Element | null = element.parentElement;
        while (elem) {
            instance = tryGetComponentByElement(elem);
            if (instance !== null) {
                throw `Element ${reprElement(
                    element
                )} does not correspond to a component. It is a child element of ${instance.toString()}`;
            }

            elem = elem.parentElement;
        }

        throw `Element ${reprElement(
            element
        )} does not correspond to a component (and none of its parent elements correspond to a component, either)`;
    }

    return instance;
}

globalThis.componentsById = componentsById; // For debugging
globalThis.getInstanceByElement = getComponentByElement; // For debugging

export function tryGetComponentByElement(
    element: Element
): ComponentBase | null {
    let component = componentsByElement.get(element as HTMLElement);
    if (component !== undefined) {
        return component;
    }

    // Components may create additional HTML elements for layouting purposes
    // (alignment, scrolling, ...), so check if this is such an element
    if (element instanceof HTMLElement) {
        let ownerId = element.dataset.ownerId;

        if (ownerId !== undefined) {
            component = componentsById[ownerId];

            if (component !== undefined) {
                return component;
            }
        }
    }

    return null;
}

export function isComponentElement(element: Element): boolean {
    return componentsByElement.has(element as HTMLElement);
}

export function getParentComponentElement(
    element: HTMLElement
): HTMLElement | null {
    let curElement = element.parentElement;

    while (curElement !== null) {
        if (isComponentElement(curElement)) {
            return curElement;
        }

        curElement = curElement.parentElement;
    }

    return null;
}

/// Given a state, return the ids of all its children
export function getChildIds(state: ComponentState): ComponentId[] {
    let result: ComponentId[] = [];

    let propertyNamesWithChildren =
        globalThis.CHILD_ATTRIBUTE_NAMES[state['_type_']!] || [];

    for (let propertyName of propertyNamesWithChildren) {
        let propertyValue = state[propertyName];

        if (Array.isArray(propertyValue)) {
            result.push(...propertyValue);
        } else if (propertyValue !== null && propertyValue !== undefined) {
            result.push(propertyValue);
        }
    }

    return result;
}

export function updateComponentStates(
    deltaStates: { [id: string]: ComponentState },
    rootComponentId: ComponentId | null
): void {
    // Modifying the DOM makes the keyboard focus get lost. Remember which
    // element had focus so we can restore it later.
    let focusedElement = document.activeElement;
    // Find the component that this HTMLElement belongs to
    while (focusedElement !== null && !isComponentElement(focusedElement)) {
        focusedElement = focusedElement.parentElement;
    }
    let focusedComponent =
        focusedElement === null
            ? null
            : getComponentByElement(focusedElement as HTMLElement);

    // Create a set to hold all latent components, so they aren't garbage
    // collected while updating the DOM.
    let latentComponents = new Set<ComponentBase>();

    // Keep track of all components whose `_grow_` changed, because their
    // parents have to be notified so they can update their CSS
    let growChangedComponents: ComponentBase[] = [];

    // Make sure all components mentioned in the message have a corresponding
    // HTML element
    for (let componentIdAsString in deltaStates) {
        let deltaState = deltaStates[componentIdAsString];
        let component = componentsById[componentIdAsString];

        // This is a reused component, no need to instantiate a new one
        if (component) {
            // Check if its `_grow_` changed
            if (deltaState._grow_ !== undefined) {
                if (
                    deltaState._grow_[0] !== component.state._grow_[0] ||
                    deltaState._grow_[1] !== component.state._grow_[1]
                ) {
                    growChangedComponents.push(component);
                }
            }
            continue;
        }

        // Get the class for this component
        const componentClass = COMPONENT_CLASSES[deltaState._type_!];

        // Make sure the component type is valid (Just helpful for debugging)
        if (!componentClass) {
            throw `Encountered unknown component type: ${deltaState._type_}`;
        }

        // Create an instance for this component
        let newComponent: ComponentBase = new componentClass(
            parseInt(componentIdAsString),
            deltaState
        );

        // Register the component for quick and easy lookup
        componentsById[componentIdAsString] = newComponent;
        componentsByElement.set(newComponent.element, newComponent);

        // Store the component's class name in the element. Used for debugging.
        newComponent.element.setAttribute(
            'dbg-py-class',
            deltaState._python_type_!
        );
        newComponent.element.setAttribute('dbg-id', componentIdAsString);

        // Set the component's key, if it has one. Used for debugging.
        let key = deltaState['key'];
        if (key !== undefined) {
            newComponent.element.setAttribute('dbg-key', `${key}`);
        }
    }

    // Update all components mentioned in the message
    for (let id in deltaStates) {
        let deltaState = deltaStates[id];
        let component: ComponentBase = componentsById[id]!;

        // Perform updates specific to this component type
        component.updateElement(deltaState, latentComponents);

        // Update the component's state
        component.state = {
            ...component.state,
            ...deltaState,
        };
    }

    // Notify the parents of all elements whose `_grow_` changed to update their
    // CSS
    let parents = new Set<ComponentBase>();
    for (let child of growChangedComponents) {
        parents.add(child.parent!);
    }
    for (let parent of parents) {
        parent.onChildGrowChanged();
    }

    // Restore the keyboard focus
    if (focusedComponent !== null) {
        restoreKeyboardFocus(focusedComponent, latentComponents);
    }

    // Remove the latent components
    for (let component of latentComponents) {
        // Destruct the component and all its children
        let queue = [component];

        for (let comp of queue) {
            queue.push(...comp.children);

            comp.onDestruction();
            delete componentsById[comp.id];
            componentsByElement.delete(comp.element);
        }
    }

    // If this is the first time, check if there's an #url-fragment and scroll
    // to it
    if (rootComponentId !== null) {
        scrollToUrlFragment('instant');
    }

    // Notify the dev tools, if any
    if (globalThis.RIO_DEV_TOOLS !== null) {
        let devToolsComponent =
            globalThis.RIO_DEV_TOOLS as DevToolsConnectorComponent;

        devToolsComponent.afterComponentStateChange(deltaStates);
    }
}

function canHaveKeyboardFocus(instance: ComponentBase): boolean {
    // @ts-expect-error
    return typeof instance.grabKeyboardFocus === 'function';
}

function restoreKeyboardFocus(
    focusedComponent: ComponentBase,
    latentComponents: Set<ComponentBase>
): void {
    // The elements that are about to die still know the id of the parent from
    // which they were just removed. We'll go up the tree until we find a parent
    // that can accept the keyboard focus.
    //
    // Keep in mind that we have to traverse the component tree all the way up to
    // the root. Because even if a component still has a parent, the parent itself
    // might be about to die.
    let rootComponent = getRootComponent();
    let current = focusedComponent;
    let winner: ComponentBase | null = null;

    while (current !== rootComponent) {
        // If this component is dead, no child of it can get the keyboard focus
        if (latentComponents.has(current)) {
            winner = null;
        }

        // If we don't currently know of a focusable (and live) component, check
        // if this one fits the bill
        else if (winner === null && canHaveKeyboardFocus(current)) {
            winner = current;
        }

        current = current.parent!;
    }

    // We made it to the root. Do we have a winner?
    if (winner !== null) {
        // @ts-expect-error
        winner.grabKeyboardFocus();
    }
}
