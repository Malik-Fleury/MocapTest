from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox

from logic.mocap.mocap_multi_kalman_filters import MocapMultiFilters
from ui.widget.common_checkbox import CommonCheckbox
from ui.widget.decimal_input import DecimalInput


class KalmanWidget(BoxLayout):
    def __init__(self, mocap_multi_filters: MocapMultiFilters, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.mocap_multi_filters = mocap_multi_filters
        self.kalman_checkbox = CommonCheckbox('Kalman Filter', False)
        self.kalman_process_noise_factor_input = DecimalInput(False)
        self.kalman_process_noise_factor_input.bind(text=self.on_process_value_changed)
        self.kalman_measure_noise_factor_input = DecimalInput(False)
        self.kalman_measure_noise_factor_input.bind(text=self.on_measure_value_changed)
        self.add_widget(self.kalman_checkbox)
        self.add_widget(self.kalman_process_noise_factor_input)
        self.add_widget(self.kalman_measure_noise_factor_input)
        self.kalman_checkbox.bind(self.on_checkbox_active_changed)
        self.size_hint = (1, None)

    def is_active(self) -> bool:
        return self.kalman_checkbox.is_active()

    def on_process_value_changed(self, instance: DecimalInput, text):
        if not instance.is_empty():
            self.mocap_filter.update_process_noise_cov(self.get_process_noise_factor())

    def on_measure_value_changed(self, instance: DecimalInput, text):
        if not instance.is_empty():
            self.mocap_filter.update_measure_noise_cov(self.get_measure_noise_factor())

    def is_kalman_active(self) -> bool:
        return self.kalman_checkbox.is_active()

    def on_checkbox_active_changed(self, checkbox: CheckBox, value: bool) -> None:
        disabled = not value
        self.kalman_process_noise_factor_input.disabled = disabled
        self.kalman_measure_noise_factor_input.disabled = disabled
