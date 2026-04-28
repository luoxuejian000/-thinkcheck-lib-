import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit';
import { window } from '@kit.ArkUI';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    console.info('[ThinkCheck4] EntryAbility onCreate');
  }
  onDestroy(): void {
    console.info('[ThinkCheck4] EntryAbility onDestroy');
  }
  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index', (err, data) => {
      if (err.code) {
        console.error('[ThinkCheck4] Failed to load content: ' + JSON.stringify(err));
        return;
      }
      console.info('[ThinkCheck4] Succeeded in loading content');
    });
  }
  onWindowStageDestroy(): void {
    console.info('[ThinkCheck4] EntryAbility onWindowStageDestroy');
  }
  onForeground(): void {
    console.info('[ThinkCheck4] EntryAbility onForeground');
  }
  onBackground(): void {
    console.info('[ThinkCheck4] EntryAbility onBackground');
  }
}